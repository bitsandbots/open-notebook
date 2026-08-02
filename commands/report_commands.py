import time
import uuid
from typing import Optional

from loguru import logger
from surreal_commands import CommandInput, CommandOutput, command

from open_notebook.domain.notebook import vector_search
from open_notebook.domain.report import Report
from open_notebook.graphs.report import graph


class GenerateReportInput(CommandInput):
    """Input for the generate_report background command."""

    notebook_id: Optional[str] = None
    source_ids: Optional[list[str]] = None
    instructions: Optional[str] = None
    style: str = "professional"


class GenerateReportOutput(CommandOutput):
    """Output from the generate_report background command."""

    success: bool
    report_id: Optional[str] = None
    word_count: Optional[int] = None
    processing_time: float


@command("generate_report", app="open_notebook", retry={"max_attempts": 2})
async def generate_report_command(
    input_data: GenerateReportInput,
) -> GenerateReportOutput:
    """Generate a report from notebook sources using the report LangGraph graph.

    Flow:
    1. Load source content (from notebook vector search or specific source IDs)
    2. Create a Report record with status "generating"
    3. Run the report graph: analyze → parallel sections → synthesize
    4. Save the final report content and update status to "draft"
    """
    start_time = time.time()

    try:
        logger.info("Starting report generation")

        # 1. Gather source content
        content_parts: list[str] = []

        if input_data.source_ids:
            # Load specific sources
            from open_notebook.database.repository import repo_query

            for source_id in input_data.source_ids:
                results = await repo_query(
                    f"SELECT * FROM source WHERE id = {source_id}"
                )
                if results:
                    source = results[0]
                    title = source.get("title", "Untitled")
                    body = source.get("content", source.get("text", ""))
                    if body:
                        content_parts.append(f"# {title}\n\n{body}")
        elif input_data.notebook_id:
            # Search across the notebook
            results = await vector_search(
                "comprehensive overview of all topics", 20, True, True
            )
            for r in results:
                title = r.get("title", "Untitled")
                body = r.get("content", r.get("text", ""))
                if body:
                    content_parts.append(f"# {title}\n\n{body}")
        else:
            raise ValueError(
                "Either notebook_id or source_ids must be provided"
            )

        if not content_parts:
            raise ValueError("No content found from the provided sources")

        content = "\n\n".join(content_parts)

        # 2. Create report record
        report_group_id = str(uuid.uuid4())
        report = Report(
            name="Generating...",
            content="",
            notebook_id=input_data.notebook_id,
            source_ids=input_data.source_ids or [],
            status="generating",
            report_group_id=report_group_id,
        )
        await report.save()
        logger.info(f"Created report record: {report.id}")

        # 3. Run the report generation graph
        initial_state = {
            "content": content,
            "instructions": input_data.instructions,
            "style": input_data.style,
        }

        result = await graph.ainvoke(initial_state)

        final_report = result.get("final_report", "")
        structure = result.get("structure")

        # Extract title from structure if available
        title = "Generated Report"
        if structure and hasattr(structure, "title"):
            title = structure.title

        # 4. Update the report record
        word_count = len(final_report.split()) if final_report else 0
        report.name = title
        report.content = final_report
        report.status = "draft"
        report.word_count = word_count
        await report.save()

        processing_time = time.time() - start_time
        logger.info(
            f"Report generation complete: {report.id} "
            f"({word_count} words, {processing_time:.1f}s)"
        )

        return GenerateReportOutput(
            success=True,
            report_id=str(report.id),
            word_count=word_count,
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Report generation failed: {e}")
        return GenerateReportOutput(
            success=False,
            processing_time=processing_time,
            error=str(e),
        )
