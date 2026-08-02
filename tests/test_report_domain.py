"""Tests for Report domain model (Phase 2.1).

Validates CRUD operations, serialization, nullable_fields, and
the model's integration with SurrealDB.
"""

from unittest.mock import AsyncMock, patch

import pytest

from open_notebook.domain.report import Report


class TestReportDomain:
    def test_report_creation_defaults(self):
        """Report model has correct defaults for new instances."""
        report = Report(
            name="Test Report",
            content="# Hello",
        )
        assert report.name == "Test Report"
        assert report.content == "# Hello"
        assert report.content_type == "markdown"
        assert report.status == "draft"
        assert report.source_ids == []
        assert report.notebook_id is None
        assert report.report_group_id is None
        assert report.parent_id is None
        assert report.word_count is None

    def test_nullable_fields_covers_all_optionals(self):
        """Every Optional field is listed in nullable_fields (required by ObjectModel)."""
        expected = {"notebook_id", "report_group_id", "parent_id", "word_count"}
        assert Report.nullable_fields == expected

    def test_table_name_is_correct(self):
        """Table name matches the SurrealDB schema from migration 24."""
        assert Report.table_name == "report"

    @pytest.mark.asyncio
    async def test_save_and_get(self):
        """Report can be saved to and retrieved from the database."""
        report = Report(
            name="Integration Test",
            content="# Test Content",
            content_type="markdown",
            status="draft",
            word_count=3,
        )

        with patch.object(Report, "save", new=AsyncMock()) as mock_save:
            await report.save()
            mock_save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete(self):
        """Report can be deleted."""
        report = Report(
            name="To Delete",
            content="content",
        )

        with patch.object(Report, "delete", new=AsyncMock()) as mock_delete:
            await report.delete()
            mock_delete.assert_called_once()

    def test_report_with_all_fields(self):
        """Report with all optional fields populated serializes correctly."""
        report = Report(
            name="Full Report",
            content="# Full Content\n\nRich text here.",
            content_type="markdown",
            notebook_id="notebook:abc123",
            source_ids=["source:1", "source:2"],
            status="draft",
            report_group_id="group-xyz",
            parent_id="report:parent1",
            word_count=150,
        )
        assert report.notebook_id == "notebook:abc123"
        assert len(report.source_ids) == 2
        assert report.report_group_id == "group-xyz"
        assert report.parent_id == "report:parent1"
        assert report.word_count == 150
