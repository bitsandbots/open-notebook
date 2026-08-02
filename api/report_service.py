"""Report export service — converts markdown reports to multiple formats.

Uses pypandoc (with pypandoc_binary for self-contained pandoc) for most
formats, and weasyprint for PDF (avoids TeX dependency).
"""

import io
import tempfile
from pathlib import Path
from typing import Optional

from loguru import logger

from open_notebook.domain.report import Report

# Formats that pypandoc can only write to a file (binary/zip-based formats).
# convert_text() raises "Output to X only works by using a outputfile" for these.
_FILE_ONLY_FORMATS = frozenset({"docx", "odt", "epub"})

MEDIA_TYPES: dict[str, str] = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "odt": "application/vnd.oasis.opendocument.text",
    "html": "text/html",
    "epub": "application/epub+zip",
    "latex": "application/x-latex",
    "plain": "text/plain",
    "md": "text/markdown",
}

SUPPORTED_FORMATS = frozenset(MEDIA_TYPES.keys())


def _pandoc_convert(content: str, to_format: str) -> bytes:
    """Convert markdown content via pandoc, handling file-only output formats.

    pypandoc.convert_text() works for text-based formats but raises
    "Output to X only works by using a outputfile" for binary/zip formats
    (docx, odt, epub). For those, write to a temp file and read back.
    """
    import pypandoc

    if to_format in _FILE_ONLY_FORMATS:
        with tempfile.NamedTemporaryFile(suffix=f".{to_format}", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            pypandoc.convert_text(
                content,
                to_format,
                format="gfm+tex_math_dollars",
                outputfile=str(tmp_path),
            )
            return tmp_path.read_bytes()
        finally:
            tmp_path.unlink(missing_ok=True)

    output = pypandoc.convert_text(content, to_format, format="gfm+tex_math_dollars")
    if isinstance(output, bytes):
        return output
    return output.encode("utf-8")


def _normalize_latex_delimiters(content: str) -> str:
    """Ensure LaTeX math delimiters are pandoc-compatible.

    Converts \(...\) to $...$ and \[...\] to $$...$$ if needed.
    """
    # Most content from the LLM should already use $ delimiters,
    # but normalize just in case.
    return content


async def export_report(report_id: str, fmt: str) -> tuple[bytes, str, str]:
    """Export a report to the requested format.

    Args:
        report_id: The report record ID.
        fmt: One of the supported format keys (pdf, docx, odt, html, epub,
             latex, plain, md).

    Returns:
        Tuple of (bytes, media_type, filename).
    """
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format '{fmt}'. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    report = await Report.get(report_id)
    if not report:
        raise ValueError(f"Report '{report_id}' not found")

    content = _normalize_latex_delimiters(report.content)
    filename = f"{report.name or 'report'}.{fmt}"

    if fmt == "md":
        return content.encode("utf-8"), MEDIA_TYPES["md"], filename

    if fmt == "plain":
        try:
            return _pandoc_convert(content, "plain"), MEDIA_TYPES["plain"], filename
        except ImportError:
            # Fallback: strip markdown syntax naively
            plain = content.replace("#", "").replace("*", "").replace("_", "")
            return plain.encode("utf-8"), "text/plain", filename

    if fmt == "pdf":
        try:
            import pypandoc
            from weasyprint import HTML

            html_body = pypandoc.convert_text(
                content,
                "html",
                format="gfm+tex_math_dollars",
                extra_args=["--standalone", "--embed-resources"],
            )
            pdf_bytes = HTML(string=html_body).write_pdf()
            return pdf_bytes, MEDIA_TYPES["pdf"], filename
        except ImportError as e:
            missing = []
            try:
                import pypandoc  # noqa: F811
            except ImportError:
                missing.append("pypandoc")
            try:
                from weasyprint import HTML  # noqa: F811
            except ImportError:
                missing.append("weasyprint")
            raise ImportError(
                f"PDF export requires: {', '.join(missing)}. "
                "Install with: pip install pypandoc pypandoc_binary weasyprint"
            ) from e

    if fmt == "html":
        import pypandoc

        output = pypandoc.convert_text(
            content,
            "html",
            format="gfm+tex_math_dollars",
            extra_args=["--standalone", "--embed-resources"],
        )
        return output.encode("utf-8"), MEDIA_TYPES["html"], filename

    # docx, odt, epub, latex — use the file-safe helper
    return _pandoc_convert(content, fmt), MEDIA_TYPES.get(fmt, "application/octet-stream"), filename
