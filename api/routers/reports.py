"""Reports API router — CRUD + generation + multi-format export."""

import io
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel
from surreal_commands import submit_command

from api.report_service import SUPPORTED_FORMATS, export_report
from commands.report_commands import GenerateReportInput
from open_notebook.domain.report import Report
from open_notebook.exceptions import NotFoundError

router = APIRouter()


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class ReportResponse(BaseModel):
    id: str
    name: str
    content: str
    content_type: str
    notebook_id: Optional[str] = None
    source_ids: list[str] = []
    status: str
    report_group_id: Optional[str] = None
    parent_id: Optional[str] = None
    word_count: Optional[int] = None
    created: Optional[str] = None
    updated: Optional[str] = None


class ReportListResponse(BaseModel):
    reports: list[ReportResponse]


class GenerateReportRequest(BaseModel):
    notebook_id: Optional[str] = None
    source_ids: Optional[list[str]] = None
    instructions: Optional[str] = None
    style: str = "professional"


class GenerateReportResponse(BaseModel):
    job_id: str
    status: str
    message: str


class UpdateReportRequest(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _report_to_response(report: Report) -> ReportResponse:
    return ReportResponse(
        id=str(report.id) if report.id else "",
        name=report.name,
        content=report.content,
        content_type=report.content_type,
        notebook_id=report.notebook_id,
        source_ids=report.source_ids,
        status=report.status,
        report_group_id=report.report_group_id,
        parent_id=report.parent_id,
        word_count=report.word_count,
        created=report.created.isoformat() if report.created else None,
        updated=report.updated.isoformat() if report.updated else None,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/reports", response_model=ReportListResponse)
async def list_reports(
    notebook_id: Optional[str] = Query(None),
):
    """List all reports, optionally filtered by notebook."""
    if notebook_id:
        from open_notebook.database.repository import repo_query

        rows = await repo_query(
            f"SELECT * FROM report WHERE notebook_id = {notebook_id} ORDER BY created DESC"
        )
    else:
        from open_notebook.database.repository import repo_query

        rows = await repo_query("SELECT * FROM report ORDER BY created DESC")

    reports = [Report(**row) for row in rows]
    return ReportListResponse(
        reports=[_report_to_response(r) for r in reports]
    )


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(report_id: str):
    """Get a single report by ID."""
    report = await Report.get(report_id)
    if not report:
        raise NotFoundError(f"Report '{report_id}' not found")
    return _report_to_response(report)


@router.patch("/reports/{report_id}", response_model=ReportResponse)
async def update_report(report_id: str, payload: UpdateReportRequest):
    """Update a report's name or content."""
    report = await Report.get(report_id)
    if not report:
        raise NotFoundError(f"Report '{report_id}' not found")

    if payload.name is not None:
        report.name = payload.name
    if payload.content is not None:
        report.content = payload.content
        report.word_count = len(payload.content.split())

    await report.save()
    return _report_to_response(report)


@router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a report."""
    report = await Report.get(report_id)
    if not report:
        raise NotFoundError(f"Report '{report_id}' not found")
    await report.delete()
    return {"message": "Report deleted", "report_id": report_id}


@router.post("/reports/generate", response_model=GenerateReportResponse)
async def generate_report(payload: GenerateReportRequest):
    """Submit a report generation job to the background worker."""
    if not payload.notebook_id and not payload.source_ids:
        raise HTTPException(
            status_code=400,
            detail="Either notebook_id or source_ids must be provided",
        )

    command_input = GenerateReportInput(
        notebook_id=payload.notebook_id,
        source_ids=payload.source_ids,
        instructions=payload.instructions,
        style=payload.style,
    )

    job = await submit_command(command_input)
    return GenerateReportResponse(
        job_id=job.id if hasattr(job, "id") else str(job),
        status="submitted",
        message="Report generation has been queued",
    )


@router.get("/reports/{report_id}/export")
async def export(report_id: str, format: str = Query("pdf")):
    """Export a report in the requested format.

    Supported formats: pdf, docx, odt, html, epub, latex, plain, md
    """
    if format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{format}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}",
        )

    try:
        data, media_type, filename = await export_report(report_id, format)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ImportError as e:
        raise HTTPException(status_code=501, detail=str(e))

    return StreamingResponse(
        io.BytesIO(data),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        },
    )
