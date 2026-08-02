from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from loguru import logger
from pydantic import BaseModel
from surreal_commands import submit_command

from api.podcast_service import (
    PodcastGenerationRequest,
    PodcastGenerationResponse,
    PodcastService,
)
from open_notebook.ai.models import Model
from open_notebook.exceptions import OpenNotebookError
from open_notebook.podcasts.audio_paths import resolve_contained_audio_path
from open_notebook.podcasts.models import PipelineStatus, PodcastEpisode

router = APIRouter()

# Model reference fields stored in the denormalized profile snapshots on an
# episode, mapped to the resolved display fields the frontend renders
# ("provider / name" rows in EpisodeCard). Mirrors the speaker_config ->
# speaker_config_name precedent in api/routers/episode_profiles.py.
_EPISODE_PROFILE_MODEL_FIELDS = {
    "outline_llm": ("outline_model_provider", "outline_model_name"),
    "transcript_llm": ("transcript_model_provider", "transcript_model_name"),
}
_SPEAKER_PROFILE_MODEL_FIELDS = {
    "voice_model": ("voice_model_provider", "voice_model_name"),
}


def _collect_snapshot_model_ids(episodes: List[PodcastEpisode]) -> List[str]:
    """Collect the distinct model record IDs referenced by episode snapshots."""
    ids = set()
    for episode in episodes:
        for field in _EPISODE_PROFILE_MODEL_FIELDS:
            ref = (episode.episode_profile or {}).get(field)
            if ref:
                ids.add(str(ref))
        for field in _SPEAKER_PROFILE_MODEL_FIELDS:
            ref = (episode.speaker_profile or {}).get(field)
            if ref:
                ids.add(str(ref))
    return sorted(ids)


def _with_resolved_model_fields(
    snapshot: dict,
    field_map: dict,
    models_by_id: dict,
) -> dict:
    """Return a copy of a profile snapshot with resolved model display fields.

    Only sets the display fields when the reference resolves; unresolvable
    references (deleted model) and legacy snapshots without references are
    left untouched so the frontend can fall back to the historical
    provider/model strings, then to a placeholder.
    """
    enriched = dict(snapshot or {})
    for ref_field, (provider_field, name_field) in field_map.items():
        ref = enriched.get(ref_field)
        info = models_by_id.get(str(ref)) if ref else None
        if info:
            enriched[provider_field] = info["provider"]
            enriched[name_field] = info["name"]
    return enriched


async def _resolve_snapshot_models(
    episodes: List[PodcastEpisode],
) -> dict:
    """Batch-resolve every model reference in the episodes' snapshots.

    One query for the whole list (see Model.get_display_info_for_ids) - a
    failure degrades to no resolved fields rather than failing the request.
    """
    try:
        return await Model.get_display_info_for_ids(
            _collect_snapshot_model_ids(episodes)
        )
    except Exception as e:
        logger.warning(f"Error batch-resolving snapshot model references: {str(e)}")
        return {}


def _delete_episode_audio(episode: PodcastEpisode, episode_id: str) -> None:
    """Best-effort unlink of an episode's audio file, refusing invalid paths.

    Shared by the delete and retry endpoints. Legacy/escaping audio_file
    values (resolve_contained_audio_path -> None) are logged and skipped.
    """
    if not episode.audio_file:
        return
    audio_path = resolve_contained_audio_path(episode.audio_file)
    if audio_path is None:
        logger.warning(
            f"Refusing to delete audio file outside podcasts directory "
            f"for episode {episode_id}: {episode.audio_file}"
        )
    elif audio_path.exists():
        try:
            audio_path.unlink()
            logger.info(f"Deleted audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to delete audio file {audio_path}: {e}")


class PodcastEpisodeResponse(BaseModel):
    id: str
    name: str
    episode_profile: dict
    speaker_profile: dict
    briefing: str
    audio_file: Optional[str] = None
    audio_url: Optional[str] = None
    transcript: Optional[dict] = None
    outline: Optional[dict] = None
    created: Optional[str] = None
    job_status: Optional[str] = None
    error_message: Optional[str] = None
    pipeline_status: Optional[str] = None


@router.post("/podcasts/generate", response_model=PodcastGenerationResponse)
async def generate_podcast(request: PodcastGenerationRequest):
    """
    Generate a podcast episode using Episode Profiles.
    Returns immediately with job ID for status tracking.
    """
    try:
        job_id = await PodcastService.submit_generation_job(
            episode_profile_name=request.episode_profile,
            speaker_profile_name=request.speaker_profile,
            episode_name=request.episode_name,
            notebook_id=request.notebook_id,
            content=request.content,
            briefing_suffix=request.briefing_suffix,
        )

        return PodcastGenerationResponse(
            job_id=job_id,
            status="submitted",
            message=f"Podcast generation started for episode '{request.episode_name}'",
            episode_profile=request.episode_profile,
            episode_name=request.episode_name,
        )

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error generating podcast: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to generate podcast"
        )


@router.get("/podcasts/jobs/{job_id}")
async def get_podcast_job_status(job_id: str):
    """Get the status of a podcast generation job"""
    try:
        status_data = await PodcastService.get_job_status(job_id)
        return status_data

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching podcast job status: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to fetch job status"
        )


@router.get("/podcasts/episodes", response_model=List[PodcastEpisodeResponse])
async def list_podcast_episodes():
    """List all podcast episodes"""
    try:
        episodes = await PodcastService.list_episodes()

        # Batch-fetch job status for every episode with a command in one
        # query instead of one round trip per episode (see
        # PodcastEpisode.get_job_details_for_commands docstring).
        try:
            details_by_command = await PodcastEpisode.get_job_details_for_commands(
                [episode.command for episode in episodes if episode.command]
            )
        except Exception as e:
            logger.warning(f"Error batch-fetching podcast job statuses: {str(e)}")
            details_by_command = {}

        # Batch-resolve the snapshots' model references (outline_llm,
        # transcript_llm, voice_model) to display fields in one query
        # instead of one lookup per episode.
        models_by_id = await _resolve_snapshot_models(episodes)

        response_episodes = []
        for episode in episodes:
            # Skip incomplete episodes without command or audio
            if not episode.command and not episode.audio_file:
                continue

            # Get job status and error message if available
            job_status = None
            error_message = None
            if episode.command:
                detail = details_by_command.get(str(episode.command))
                if detail is not None:
                    job_status = detail["status"]
                    error_message = detail["error_message"]
                else:
                    job_status = "unknown"
            else:
                # No command but has audio file = completed import
                job_status = "completed"

            audio_url = None
            audio_path = resolve_contained_audio_path(episode.audio_file)
            if audio_path is not None and audio_path.exists():
                audio_url = f"/api/podcasts/episodes/{episode.id}/audio"

            response_episodes.append(
                PodcastEpisodeResponse(
                    id=str(episode.id),
                    name=episode.name,
                    episode_profile=_with_resolved_model_fields(
                        episode.episode_profile,
                        _EPISODE_PROFILE_MODEL_FIELDS,
                        models_by_id,
                    ),
                    speaker_profile=_with_resolved_model_fields(
                        episode.speaker_profile,
                        _SPEAKER_PROFILE_MODEL_FIELDS,
                        models_by_id,
                    ),
                    briefing=episode.briefing,
                    audio_file=episode.audio_file,
                    audio_url=audio_url,
                    transcript=episode.transcript,
                    outline=episode.outline,
                    created=str(episode.created) if episode.created else None,
                    job_status=job_status,
                    error_message=error_message,
                    pipeline_status=episode.pipeline_status,
                )
            )

        return response_episodes

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error listing podcast episodes: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to list podcast episodes"
        )


@router.get("/podcasts/episodes/{episode_id}", response_model=PodcastEpisodeResponse)
async def get_podcast_episode(episode_id: str):
    """Get a specific podcast episode"""
    try:
        episode = await PodcastService.get_episode(episode_id)

        # Get job status and error message if available
        job_status = None
        error_message = None
        if episode.command:
            try:
                detail = await episode.get_job_detail()
                job_status = detail["status"]
                error_message = detail["error_message"]
            except Exception:
                job_status = "unknown"
        else:
            # No command but has audio file = completed import
            job_status = "completed" if episode.audio_file else "unknown"

        audio_url = None
        audio_path = resolve_contained_audio_path(episode.audio_file)
        if audio_path is not None and audio_path.exists():
            audio_url = f"/api/podcasts/episodes/{episode.id}/audio"

        models_by_id = await _resolve_snapshot_models([episode])

        return PodcastEpisodeResponse(
            id=str(episode.id),
            name=episode.name,
            episode_profile=_with_resolved_model_fields(
                episode.episode_profile,
                _EPISODE_PROFILE_MODEL_FIELDS,
                models_by_id,
            ),
            speaker_profile=_with_resolved_model_fields(
                episode.speaker_profile,
                _SPEAKER_PROFILE_MODEL_FIELDS,
                models_by_id,
            ),
            briefing=episode.briefing,
            audio_file=episode.audio_file,
            audio_url=audio_url,
            transcript=episode.transcript,
            outline=episode.outline,
            created=str(episode.created) if episode.created else None,
            job_status=job_status,
            error_message=error_message,
            pipeline_status=episode.pipeline_status,
        )

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching podcast episode: {str(e)}")
        raise HTTPException(status_code=404, detail="Episode not found")


@router.get("/podcasts/episodes/{episode_id}/audio")
async def stream_podcast_episode_audio(episode_id: str):
    """Stream the audio file associated with a podcast episode"""
    try:
        episode = await PodcastService.get_episode(episode_id)
    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching podcast episode for audio: {str(e)}")
        raise HTTPException(status_code=404, detail="Episode not found")

    if not episode.audio_file:
        raise HTTPException(status_code=404, detail="Episode has no audio file")

    audio_path = resolve_contained_audio_path(episode.audio_file)
    if audio_path is None:
        logger.warning(
            f"Blocked audio access outside podcasts directory for episode "
            f"{episode_id}: {episode.audio_file}"
        )
        raise HTTPException(status_code=403, detail="Access to file denied")

    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=audio_path.name,
    )


@router.post("/podcasts/episodes/{episode_id}/retry")
async def retry_podcast_episode(episode_id: str):
    """Retry a failed podcast episode by deleting it and submitting a new job"""
    try:
        episode = await PodcastService.get_episode(episode_id)

        # Validate episode is in a failed state
        detail = await episode.get_job_detail()
        if detail["status"] not in ("failed", "error"):
            raise HTTPException(
                status_code=400,
                detail=f"Episode is not in a failed state (current: {detail['status']})",
            )

        # Extract params for re-submission
        ep_profile_name = episode.episode_profile.get("name")
        sp_profile_name = episode.speaker_profile.get("name")
        episode_name = episode.name
        content = episode.content

        if not ep_profile_name or not sp_profile_name:
            raise HTTPException(
                status_code=400,
                detail="Cannot retry: episode or speaker profile name missing from stored data",
            )

        # Delete audio file if any
        _delete_episode_audio(episode, episode_id)

        # Delete the failed episode
        await episode.delete()

        # Submit a new job
        job_id = await PodcastService.submit_generation_job(
            episode_profile_name=ep_profile_name,
            speaker_profile_name=sp_profile_name,
            episode_name=episode_name,
            content=content,
        )

        return {"job_id": job_id, "message": "Retry submitted successfully"}

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error retrying podcast episode: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retry episode"
        )


@router.delete("/podcasts/episodes/{episode_id}")
async def delete_podcast_episode(episode_id: str):
    """Delete a podcast episode and its associated audio file"""
    try:
        # Get the episode first to check if it exists and get the audio file path
        episode = await PodcastService.get_episode(episode_id)

        # Delete the physical audio file if it exists
        _delete_episode_audio(episode, episode_id)

        # Delete the episode from the database
        await episode.delete()

        logger.info(f"Deleted podcast episode: {episode_id}")
        return {"message": "Episode deleted successfully", "episode_id": episode_id}

    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error deleting podcast episode: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to delete episode"
        )


# ---------------------------------------------------------------------------
# Draft review endpoints — two-phase generation (draft → review → render)
# ---------------------------------------------------------------------------


class DraftResponse(BaseModel):
    """Transcript + outline for the draft review UI."""

    episode_id: str
    name: str
    pipeline_status: Optional[str] = None
    transcript: Optional[Dict[str, Any]] = None
    outline: Optional[Dict[str, Any]] = None
    briefing: str


class DraftUpdateRequest(BaseModel):
    """User edits to the transcript before rendering."""

    transcript: Optional[Dict[str, Any]] = None


@router.get("/podcasts/episodes/{episode_id}/draft", response_model=DraftResponse)
async def get_episode_draft(episode_id: str):
    """Return the transcript + outline for review before rendering."""
    try:
        episode = await PodcastService.get_episode(episode_id)
        return DraftResponse(
            episode_id=str(episode.id),
            name=episode.name,
            pipeline_status=episode.pipeline_status,
            transcript=episode.transcript,
            outline=episode.outline,
            briefing=episode.briefing,
        )
    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error fetching episode draft: {str(e)}")
        raise HTTPException(status_code=404, detail="Episode not found")


@router.patch("/podcasts/episodes/{episode_id}/draft")
async def update_episode_draft(episode_id: str, request: DraftUpdateRequest):
    """Save user edits to the transcript before rendering."""
    try:
        episode = await PodcastService.get_episode(episode_id)

        if episode.pipeline_status not in (
            PipelineStatus.DRAFT_READY.value,
            None,  # legacy episodes
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Episode is not in draft_ready state "
                f"(current: {episode.pipeline_status})",
            )

        if request.transcript is not None:
            episode.transcript = request.transcript
            await episode.save()

        return {"message": "Draft updated successfully", "episode_id": episode_id}
    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error updating episode draft: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update draft")


@router.post("/podcasts/episodes/{episode_id}/approve")
async def approve_episode_draft(episode_id: str):
    """Approve the draft and dispatch the render command (TTS + audio)."""
    try:
        episode = await PodcastService.get_episode(episode_id)

        if episode.pipeline_status not in (
            PipelineStatus.DRAFT_READY.value,
            None,  # legacy episodes
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Episode is not ready for approval "
                f"(current: {episode.pipeline_status})",
            )

        # Ensure command modules are imported before submitting
        try:
            import commands.podcast_commands  # noqa: F401
        except ImportError:
            raise HTTPException(
                status_code=500, detail="Podcast commands not available"
            )

        job_id = submit_command(
            "open_notebook",
            "render_podcast",
            {"episode_id": episode_id},
        )

        logger.info(
            f"Dispatched render_podcast job {job_id} for episode {episode_id}"
        )
        return {
            "job_id": str(job_id),
            "message": "Render job submitted successfully",
            "episode_id": episode_id,
        }
    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error approving episode draft: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve draft")


@router.post("/podcasts/episodes/{episode_id}/cancel")
async def cancel_episode_generation(episode_id: str):
    """Cancel an in-progress episode generation."""
    try:
        episode = await PodcastService.get_episode(episode_id)

        if episode.pipeline_status not in (
            PipelineStatus.DRAFTING.value,
            PipelineStatus.DRAFT_READY.value,
            PipelineStatus.RENDERING.value,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Episode is not in a cancellable state "
                f"(current: {episode.pipeline_status})",
            )

        episode.pipeline_status = PipelineStatus.CANCELLED.value
        await episode.save()

        return {"message": "Episode cancelled", "episode_id": episode_id}
    except HTTPException:
        raise
    except OpenNotebookError:
        raise
    except Exception as e:
        logger.error(f"Error cancelling episode: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel episode")


# ---------------------------------------------------------------------------
# Voice preview — test a TTS voice before full generation
# ---------------------------------------------------------------------------


class VoicePreviewRequest(BaseModel):
    voice_model_id: str
    voice_id: str
    text: str = "Hello, this is a preview of how this voice sounds."


@router.post("/podcasts/voices/preview")
async def preview_voice(request: VoicePreviewRequest):
    """Generate a short TTS preview for a voice.

    Resolves the Model record to get provider/model/config, creates a TTS
    model via esperanto's AIFactory, and returns the audio as MP3 bytes.
    """
    import io

    from esperanto import AIFactory

    from open_notebook.ai.models import Model
    from open_notebook.podcasts.models import _resolve_model_config

    try:
        # Resolve the voice model record
        provider, model_name, config = await _resolve_model_config(
            request.voice_model_id
        )

        # Create TTS model via esperanto
        tts_model = AIFactory.create_text_to_speech(
            provider, model_name, **config
        )

        # Generate preview audio
        audio_buffer = io.BytesIO()
        await tts_model.agenerate_speech(
            text=request.text,
            voice_id=request.voice_id,
            output_buffer=audio_buffer,
        )
        audio_buffer.seek(0)

        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=voice-preview.mp3"},
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Voice preview failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate voice preview: {str(e)}",
        )


# ---------------------------------------------------------------------------
# Brief proposal — LLM proposes episode settings from source content
# ---------------------------------------------------------------------------


class BriefProposalRequest(BaseModel):
    content: str
    episode_profile_name: str


class BriefProposalResponse(BaseModel):
    language: str = "en-US"
    num_segments: int = 5
    briefing: str = ""


@router.post("/podcasts/propose-brief", response_model=BriefProposalResponse)
async def propose_brief(request: BriefProposalRequest):
    """Ask the LLM to propose language, segment count, and briefing.

    Uses the episode profile's outline_llm model. Returns a proposal the
    user can review before triggering full draft generation.
    """
    import json

    from open_notebook.ai.prompter import Prompter
    from open_notebook.podcasts.models import EpisodeProfile

    try:
        episode_profile = await EpisodeProfile.get_by_name(
            request.episode_profile_name
        )
        if not episode_profile:
            raise HTTPException(
                status_code=404,
                detail=f"Episode profile '{request.episode_profile_name}' not found",
            )

        if not episode_profile.outline_llm:
            raise HTTPException(
                status_code=400,
                detail="Episode profile has no outline model configured",
            )

        # Resolve the model
        provider, model_name, config = await episode_profile.resolve_outline_config()

        # Build the prompt
        prompter = Prompter(prompt_template="podcast/brief_proposal")
        messages = prompter.build_messages(
            data={"content": request.content}
        )

        # Call the LLM
        from esperanto import AIFactory

        model = AIFactory.create_language(provider, model_name, **config)
        response = await model.ainvoke(messages)

        # Parse the JSON response
        content = response.content if hasattr(response, "content") else str(response)
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        proposal = json.loads(content)

        return BriefProposalResponse(
            language=proposal.get("language", "en-US"),
            num_segments=proposal.get("num_segments", 5),
            briefing=proposal.get("briefing", ""),
        )

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse brief proposal JSON: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to parse LLM response for brief proposal",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Brief proposal failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate brief proposal: {str(e)}",
        )
