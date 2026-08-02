import operator
from typing import Annotated, List, Optional

from ai_prompter import Prompter
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from open_notebook.ai.provision import provision_langchain_model
from open_notebook.exceptions import OpenNotebookError
from open_notebook.utils import clean_thinking_content
from open_notebook.utils.error_classifier import classify_error
from open_notebook.utils.text_utils import extract_text_content


class Section(BaseModel):
    """A single section in the report structure."""

    title: str = Field(description="Section title")
    description: str = Field(
        description="What this section should cover, used as guidance for the writer"
    )


class ReportStructure(BaseModel):
    """Proposed report structure from source analysis."""

    title: str = Field(description="Proposed report title")
    sections: List[Section] = Field(
        default_factory=list,
        description="Ordered list of sections for the report",
    )


class SectionContent(BaseModel):
    """Generated content for a single section."""

    title: str = Field(description="Section title")
    content: str = Field(description="Section body in markdown")


class SectionWriterState(TypedDict):
    """State passed to each parallel section writer."""

    title: str
    description: str
    source_context: str
    style: str


class ThreadState(TypedDict):
    """Top-level state for the report generation graph."""

    content: str
    instructions: Optional[str]
    style: str
    structure: ReportStructure
    sections: Annotated[list, operator.add]
    final_report: str


async def analyze_sources(state: ThreadState, config: RunnableConfig) -> dict:
    """Analyze source content and propose a report structure."""
    try:
        parser: PydanticOutputParser[ReportStructure] = PydanticOutputParser(
            pydantic_object=ReportStructure
        )
        system_prompt = Prompter(
            prompt_template="report/analyze", parser=parser
        ).render(
            data={
                "content": state["content"],
                "instructions": state.get("instructions"),
            }
        )
        model = await provision_langchain_model(
            system_prompt,
            config.get("configurable", {}).get("strategy_model"),
            "tools",
            max_tokens=2000,
            structured=dict(type="json"),
        )
        ai_message = await model.ainvoke(system_prompt)
        message_content = extract_text_content(ai_message.content)
        cleaned_content = clean_thinking_content(message_content)
        structure = parser.parse(cleaned_content)
        return {"structure": structure}
    except OpenNotebookError:
        raise
    except Exception as e:
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e


async def dispatch_sections(state: ThreadState, config: RunnableConfig):
    """Fan out: dispatch one writer per section in parallel."""
    return [
        Send(
            "write_section",
            {
                "title": section.title,
                "description": section.description,
                "source_context": state["content"],
                "style": state.get("style", "professional"),
            },
        )
        for section in state["structure"].sections
    ]


async def write_section(state: SectionWriterState, config: RunnableConfig) -> dict:
    """Write a single report section from source context."""
    try:
        system_prompt = Prompter(prompt_template="report/section").render(
            data={
                "section_title": state["title"],
                "section_description": state["description"],
                "source_context": state["source_context"],
                "style": state.get("style", "professional"),
            }
        )
        model = await provision_langchain_model(
            system_prompt,
            config.get("configurable", {}).get("answer_model"),
            "tools",
            max_tokens=4000,
        )
        ai_message = await model.ainvoke(system_prompt)
        ai_content = extract_text_content(ai_message.content)
        return {
            "sections": [
                {
                    "title": state["title"],
                    "content": clean_thinking_content(ai_content),
                }
            ]
        }
    except OpenNotebookError:
        raise
    except Exception as e:
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e


async def synthesize_report(state: ThreadState, config: RunnableConfig) -> dict:
    """Combine all sections into a final polished report."""
    try:
        system_prompt = Prompter(prompt_template="report/synthesize").render(
            data={
                "title": state["structure"].title,
                "sections": state["sections"],
            }
        )
        model = await provision_langchain_model(
            system_prompt,
            config.get("configurable", {}).get("final_answer_model"),
            "tools",
            max_tokens=8000,
        )
        ai_message = await model.ainvoke(system_prompt)
        final_content = extract_text_content(ai_message.content)
        return {"final_report": clean_thinking_content(final_content)}
    except OpenNotebookError:
        raise
    except Exception as e:
        error_class, user_message = classify_error(e)
        raise error_class(user_message) from e


agent_state = StateGraph(ThreadState)
agent_state.add_node("analyze_sources", analyze_sources)
agent_state.add_node("write_section", write_section)
agent_state.add_node("synthesize_report", synthesize_report)
agent_state.add_edge(START, "analyze_sources")
agent_state.add_conditional_edges(
    "analyze_sources", dispatch_sections, ["write_section"]
)
agent_state.add_edge("write_section", "synthesize_report")
agent_state.add_edge("synthesize_report", END)

graph = agent_state.compile()
