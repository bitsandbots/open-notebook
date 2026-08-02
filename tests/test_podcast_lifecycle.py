"""Tests for podcast lifecycle state machine (Phase 1.1).

Validates PipelineStatus transitions, draft/render command handoff, and
the legacy monolithic command's delegation to draft + render.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from commands.podcast_commands import (
    DraftPodcastInput,
    DraftPodcastOutput,
    RenderPodcastInput,
    RenderPodcastOutput,
    PodcastGenerationInput,
    PodcastGenerationOutput,
    draft_podcast_command,
    render_podcast_command,
    generate_podcast_command,
)
from open_notebook.podcasts.models import PipelineStatus


# ---------------------------------------------------------------------------
# PipelineStatus enum
# ---------------------------------------------------------------------------


class TestPipelineStatus:
    def test_all_expected_states_exist(self):
        """Every state from the plan's state machine is present."""
        expected = {"drafting", "draft_ready", "rendering", "completed", "failed", "cancelled"}
        actual = {member.value for member in PipelineStatus}
        assert actual == expected

    def test_values_match_plan(self):
        """State values match the snake_case convention used in the DB."""
        assert PipelineStatus.DRAFTING.value == "drafting"
        assert PipelineStatus.DRAFT_READY.value == "draft_ready"
        assert PipelineStatus.RENDERING.value == "rendering"
        assert PipelineStatus.COMPLETED.value == "completed"
        assert PipelineStatus.FAILED.value == "failed"
        assert PipelineStatus.CANCELLED.value == "cancelled"


# ---------------------------------------------------------------------------
# Draft command — outline + transcript, no TTS
# ---------------------------------------------------------------------------


class TestDraftPodcastCommand:
    @pytest.mark.asyncio
    async def test_draft_input_model(self):
        """DraftPodcastInput accepts the expected fields."""
        input_data = DraftPodcastInput(
            episode_profile="Test Episode",
            speaker_profile="speaker_profile:test_speaker",
            episode_name="Test Draft",
            content="test content",
            briefing_suffix="extra instructions",
        )
        assert input_data.episode_profile == "Test Episode"
        assert input_data.speaker_profile == "speaker_profile:test_speaker"
        assert input_data.episode_name == "Test Draft"
        assert input_data.content == "test content"
        assert input_data.briefing_suffix == "extra instructions"

    @pytest.mark.asyncio
    async def test_draft_output_model(self):
        """DraftPodcastOutput carries episode_id for render handoff."""
        output = DraftPodcastOutput(
            success=True,
            episode_id="episode:test123",
            transcript={"transcript": {}},
            outline={"sections": []},
            processing_time=1.5,
        )
        assert output.success is True
        assert output.episode_id == "episode:test123"
        assert output.transcript is not None
        assert output.outline is not None
        assert output.processing_time == 1.5

    @pytest.mark.asyncio
    async def test_draft_fails_without_outline_model(self):
        """Draft command raises ValueError when episode profile has no outline model."""
        from open_notebook.podcasts.models import EpisodeProfile, SpeakerProfile

        ep_profile = Mock()
        ep_profile.name = "Test Episode"
        ep_profile.speaker_config = "speaker_profile:test_speaker"
        ep_profile.outline_llm = None  # Missing!
        ep_profile.transcript_llm = "model:transcript"
        ep_profile.default_briefing = "Default briefing"

        sp_profile = Mock()
        sp_profile.name = "Test Speaker"
        sp_profile.voice_model = "model:tts"

        with (
            patch.object(EpisodeProfile, "get_by_name", new=AsyncMock(return_value=ep_profile)),
            patch.object(SpeakerProfile, "resolve", new=AsyncMock(return_value=sp_profile)),
        ):
            with pytest.raises(ValueError, match="outline model"):
                await draft_podcast_command(DraftPodcastInput(
                    episode_profile="Test Episode",
                    speaker_profile="speaker_profile:test_speaker",
                    episode_name="Test Draft",
                    content="test content",
                ))


# ---------------------------------------------------------------------------
# Render command — TTS + audio from approved draft
# ---------------------------------------------------------------------------


class TestRenderPodcastCommand:
    @pytest.mark.asyncio
    async def test_render_rejects_non_draft_ready_episode(self):
        """Render command refuses episodes not in draft_ready state."""
        from open_notebook.podcasts.models import PodcastEpisode

        episode = Mock()
        episode.pipeline_status = "rendering"  # Not draft_ready

        with patch.object(PodcastEpisode, "get", new=AsyncMock(return_value=episode)):
            with pytest.raises(ValueError, match="not ready for rendering"):
                await render_podcast_command(RenderPodcastInput(
                    episode_id="episode:test123"
                ))

    @pytest.mark.asyncio
    async def test_render_input_model(self):
        """RenderPodcastInput accepts episode_id for draft-to-render handoff."""
        input_data = RenderPodcastInput(episode_id="episode:test123")
        assert input_data.episode_id == "episode:test123"

    @pytest.mark.asyncio
    async def test_render_output_model(self):
        """RenderPodcastOutput carries audio_file_path on success."""
        output = RenderPodcastOutput(
            success=True,
            episode_id="episode:test123",
            audio_file_path="podcasts/test/audio.mp3",
            processing_time=2.0,
        )
        assert output.success is True
        assert output.audio_file_path == "podcasts/test/audio.mp3"
        assert output.processing_time == 2.0


# ---------------------------------------------------------------------------
# Legacy monolithic command — delegates to draft + render
# ---------------------------------------------------------------------------


class TestLegacyGenerateCommand:
    @pytest.mark.asyncio
    async def test_legacy_command_delegates_to_draft_and_render(self):
        """The legacy generate_podcast command calls draft then render internally."""
        draft_result = DraftPodcastOutput(
            success=True,
            episode_id="episode:test123",
            processing_time=1.0,
        )
        render_result = RenderPodcastOutput(
            success=True,
            episode_id="episode:test123",
            audio_file_path="podcasts/test/audio.mp3",
            processing_time=2.0,
        )

        with (
            patch("commands.podcast_commands.draft_podcast_command", new=AsyncMock(return_value=draft_result)),
            patch("commands.podcast_commands.render_podcast_command", new=AsyncMock(return_value=render_result)),
        ):
            result = await generate_podcast_command(PodcastGenerationInput(
                episode_profile="Test Episode",
                speaker_profile="speaker_profile:test_speaker",
                episode_name="Test Legacy",
                content="test content",
            ))

            assert isinstance(result, PodcastGenerationOutput)
            assert result.success is True
            assert result.episode_id == "episode:test123"
            assert result.audio_file_path == "podcasts/test/audio.mp3"

    @pytest.mark.asyncio
    async def test_legacy_command_fails_when_draft_fails(self):
        """Legacy command raises when draft phase fails."""
        draft_result = DraftPodcastOutput(
            success=False,
            processing_time=1.0,
        )

        with (
            patch("commands.podcast_commands.draft_podcast_command", new=AsyncMock(return_value=draft_result)),
        ):
            with pytest.raises(RuntimeError, match="Draft phase failed"):
                await generate_podcast_command(PodcastGenerationInput(
                    episode_profile="Test Episode",
                    speaker_profile="speaker_profile:test_speaker",
                    episode_name="Test Legacy",
                    content="test content",
                ))
