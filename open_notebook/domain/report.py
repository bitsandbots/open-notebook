from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from open_notebook.domain.base import ObjectModel


class Report(ObjectModel):
    """AI-generated report from notebook sources.

    Supports versioning via report_group_id (shared across versions) and
    parent_id (points to previous version). Content is stored as markdown
    and can be exported to multiple formats.
    """

    table_name: ClassVar[str] = "report"
    nullable_fields: ClassVar[set[str]] = {
        "notebook_id",
        "report_group_id",
        "parent_id",
        "word_count",
    }

    name: str = Field(..., description="Report title")
    content: str = Field(default="", description="Report body in markdown")
    content_type: str = Field(default="markdown", description="Content format")
    notebook_id: Optional[str] = Field(
        default=None, description="Source notebook record ID"
    )
    source_ids: list[str] = Field(
        default_factory=list, description="Source record IDs used for generation"
    )
    status: str = Field(default="draft", description="Report status")
    report_group_id: Optional[str] = Field(
        default=None, description="UUID shared across versions of the same report"
    )
    parent_id: Optional[str] = Field(
        default=None, description="Previous version of this report"
    )
    word_count: Optional[int] = Field(
        default=None, description="Approximate word count of content"
    )
    created: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated: Optional[datetime] = Field(
        default=None, description="Last update timestamp"
    )
