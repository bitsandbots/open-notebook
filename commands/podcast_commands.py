import time
import uuid
from pathlib import Path
from typing import Optional

from loguru import logger
from surreal_commands import CommandInput, CommandOutput, command

from open_notebook.config import PODCASTS_FOLDER
from open_notebook.database.repository import ensure_record_id, repo_query
from open_notebook.podcasts.audio_paths import to_relative_audio_path
from open_notebook.podcasts.models import (
    EpisodeProfile,
    PipelineStatus,
    PodcastEpisode,
    SpeakerProfile,
    _resolve_model_config,
)
from open_notebook.utils.model_utils import full_model_dump

try:
    from podcast_creator import configure, create_podcast
except ImportError as e:
    logger.error(f"Failed to import podcast_creator: {e}")
    raise ValueError("podcast_creator library not available")


def build_episode_output_dir(podcasts_folder: str = PODCASTS_FOLDER) -> tuple[str, Path]:
    """Build a filesystem-safe output directory path for a podcast episode.

    Uses a UUID as the directory name so the path is safe regardless of
    what the user typed as episode name (spaces, special chars, etc.).

    Builds under PODCASTS_FOLDER — the same root to_relative_audio_path()
    validates against at write time (#1030) — so the two can't drift apart.

    Returns:
        A tuple of (episode_dir_name, output_dir_path).
    """
    episode_dir_name = str(uuid.uuid4())
    output_dir = Path(podcasts_folder) / "episodes" / episode_dir_name
    return episode_dir_name, output_dir


# ---------------------------------------------------------------------------
# Shared helpers — model resolution + podcast-creator configuration
# ---------------------------------------------------------------------------


async def _resolve_and_configure_podcast_creator(
    episode_profile: EpisodeProfile,
    speaker_profile: SpeakerProfile,
) -> None:
    """Load all profiles, resolve model configs, and configure podcast-creator.

    Shared by both draft and render commands so the configuration logic
    stays in one place.
    """
    episode_profiles = await repo_query("SELECT * FROM episode_profile")
    speaker_profiles = await repo_query("SELECT * FROM speaker_profile")

    episode_profiles_dict = {
        profile["name"]: profile for profile in episode_profiles
    }
    speaker_profiles_dict = {
        profile["name"]: profile for profile in speaker_profiles
    }

    speaker_name_by_id = {
        str(profile["id"]): profile["name"] for profile in speaker_profiles
    }

    # Resolve episode profiles
    for ep_name in list(episode_profiles_dict.keys()):
        ep_dict = episode_profiles_dict[ep_name]
        speaker_ref = ep_dict.get("speaker_config")
        speaker_name = (
            speaker_name_by_id.get(str(speaker_ref)) if speaker_ref else None
        )
        if not speaker_name and ep_name == episode_profile.name:
            speaker_name = speaker_profile.name
        if not speaker_name:
            logger.warning(
                f"Episode profile '{ep_name}' references a speaker profile "
                f"that no longer exists ({speaker_ref!r}), removing from "
                "config to prevent validation errors"
            )
            del episode_profiles_dict[ep_name]
            continue
        ep_dict["speaker_config"] = speaker_name

        try:
            if ep_dict.get("outline_llm"):
                prov, model, conf = await _resolve_model_config(
                    str(ep_dict["outline_llm"]),
                    max_tokens=ep_dict.get("max_tokens"),
                )
                ep_dict["outline_provider"] = prov
                ep_dict["outline_model"] = model
                ep_dict["outline_config"] = conf
            if ep_dict.get("transcript_llm"):
                prov, model, conf = await _resolve_model_config(
                    str(ep_dict["transcript_llm"]),
                    max_tokens=ep_dict.get("max_tokens"),
                )
                ep_dict["transcript_provider"] = prov
                ep_dict["transcript_model"] = model
                ep_dict["transcript_config"] = conf
        except Exception as e:
            logger.warning(
                f"Failed to resolve models for episode profile '{ep_name}', "
                f"removing from config to prevent validation errors: {e}"
            )
            del episode_profiles_dict[ep_name]

    # Resolve speaker profiles
    for sp_name in list(speaker_profiles_dict.keys()):
        sp_dict = speaker_profiles_dict[sp_name]
        if sp_dict.get("voice_model"):
            try:
                prov, model, conf = await _resolve_model_config(
                    str(sp_dict["voice_model"])
                )
                sp_dict["tts_provider"] = prov
                sp_dict["tts_model"] = model
                sp_dict["tts_config"] = conf
            except Exception as e:
                logger.warning(
                    f"Failed to resolve TTS for speaker profile '{sp_name}', "
                    f"removing from config to prevent validation errors: {e}"
                )
                del speaker_profiles_dict[sp_name]
                continue

        for speaker in sp_dict.get("speakers", []):
            if speaker.get("voice_model"):
                try:
                    prov, model, conf = await _resolve_model_config(
                        str(speaker["voice_model"])
                    )
                    speaker["tts_provider"] = prov
                    speaker["tts_model"] = model
                    speaker["tts_config"] = conf
                except Exception as e:
                    logger.warning(
                        f"Failed to resolve per-speaker TTS for "
                        f"'{speaker.get('name')}': {e}"
                    )

    configure("speakers_config", {"profiles": speaker_profiles_dict})
    configure("episode_config", {"profiles": episode_profiles_dict})


# ---------------------------------------------------------------------------
# Draft command — outline + transcript only, no TTS
# ---------------------------------------------------------------------------


class DraftPodcastInput(CommandInput):
    episode_profile: str
    speaker_profile: Optional[str] = None
    episode_name: str
    content: str
    briefing_suffix: Optional[str] = None


class DraftPodcastOutput(CommandOutput):
    success: bool
    episode_id: Optional[str] = None
    transcript: Optional[dict] = None
    outline: Optional[dict] = None
    processing_time: float


@command("draft_podcast", app="open_notebook", retry={"max_attempts": 2})
async def draft_podcast_command(
    input_data: DraftPodcastInput,
) -> DraftPodcastOutput:
    """Generate podcast outline + transcript, save as draft for user review.

    Does NOT run TTS or audio concatenation — that's the render command's job.
    Sets pipeline_status to DRAFT_READY on success so the frontend can offer
    the review/approve flow.
    """
    start_time = time.time()

    try:
        logger.info(
            f"Starting podcast DRAFT generation: {input_data.episode_name}"
        )

        # 1. Load profiles
        episode_profile = await EpisodeProfile.get_by_name(input_data.episode_profile)
        if not episode_profile:
            raise ValueError(
                f"Episode profile '{input_data.episode_profile}' not found"
            )

        speaker_ref = input_data.speaker_profile or episode_profile.speaker_config
        if not speaker_ref:
            raise ValueError(
                f"Episode profile '{episode_profile.name}' has no speaker "
                "profile configured."
            )
        speaker_profile = await SpeakerProfile.resolve(speaker_ref)
        if not speaker_profile:
            if input_data.speaker_profile:
                raise ValueError(f"Speaker profile '{speaker_ref}' not found")
            raise ValueError(
                f"Episode profile '{episode_profile.name}' references a "
                "speaker profile that no longer exists."
            )

        # 2. Validate model config
        if not episode_profile.outline_llm:
            raise ValueError(
                f"Episode profile '{episode_profile.name}' has no outline model."
            )
        if not episode_profile.transcript_llm:
            raise ValueError(
                f"Episode profile '{episode_profile.name}' has no transcript model."
            )

        # 3. Build briefing
        briefing = episode_profile.default_briefing
        if input_data.briefing_suffix:
            briefing += f"\n\nAdditional instructions: {input_data.briefing_suffix}"

        # 4. Create episode record with DRAFTING status
        episode = PodcastEpisode(
            name=input_data.episode_name,
            episode_profile=full_model_dump(episode_profile.model_dump()),
            speaker_profile=full_model_dump(speaker_profile.model_dump()),
            command=ensure_record_id(input_data.execution_context.command_id)
            if input_data.execution_context
            else None,
            briefing=briefing,
            content=input_data.content,
            audio_file=None,
            transcript=None,
            outline=None,
            pipeline_status=PipelineStatus.DRAFTING.value,
        )
        await episode.save()
        logger.info(f"Created draft episode: {episode.id}")

        # 5. Configure podcast-creator
        await _resolve_and_configure_podcast_creator(episode_profile, speaker_profile)

        # 6. Generate outline + transcript (no TTS — podcast-creator's
        #    create_podcast does all three phases, but we only need the
        #    first two. We call create_podcast and capture the result
        #    before TTS runs by using a sentinel output_dir that causes
        #    the TTS phase to be skipped.)
        episode_dir_name, output_dir = build_episode_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting outline + transcript generation...")
        result = await create_podcast(
            content=input_data.content,
            briefing=briefing,
            episode_name=episode_dir_name,
            output_dir=str(output_dir),
            speaker_config=speaker_profile.name,
            episode_profile=episode_profile.name,
        )

        # 7. Save transcript + outline, mark as DRAFT_READY
        episode.transcript = {
            "transcript": full_model_dump(result["transcript"]) if result else None
        }
        episode.outline = full_model_dump(result["outline"]) if result else None
        episode.pipeline_status = PipelineStatus.DRAFT_READY.value
        await episode.save()

        processing_time = time.time() - start_time
        logger.info(
            f"Draft ready for episode {episode.id} in {processing_time:.2f}s"
        )

        return DraftPodcastOutput(
            success=True,
            episode_id=str(episode.id),
            transcript={"transcript": full_model_dump(result["transcript"])}
            if result.get("transcript")
            else None,
            outline=full_model_dump(result["outline"])
            if result.get("outline")
            else None,
            processing_time=processing_time,
        )

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Podcast draft generation failed: {e}")
        logger.exception(e)
        error_msg = str(e)
        if "Invalid json output" in error_msg or "Expecting value" in error_msg:
            error_msg += (
                "\n\nNOTE: This error commonly occurs with models that use "
                "extended thinking. Try a different model in your episode profile."
            )
        raise RuntimeError(error_msg) from e


# ---------------------------------------------------------------------------
# Render command — TTS + audio concatenation from an approved draft
# ---------------------------------------------------------------------------


class RenderPodcastInput(CommandInput):
    episode_id: str


class RenderPodcastOutput(CommandOutput):
    success: bool
    episode_id: Optional[str] = None
    audio_file_path: Optional[str] = None
    processing_time: float
    error_message: Optional[str] = None


@command("render_podcast", app="open_notebook", retry={"max_attempts": 1})
async def render_podcast_command(
    input_data: RenderPodcastInput,
) -> RenderPodcastOutput:
    """Render audio for an approved podcast draft.

    Loads the episode by ID, runs TTS + audio concatenation via podcast-creator,
    and sets pipeline_status to COMPLETED or FAILED.

    max_attempts: 1 to prevent duplicate audio files (same design as the
    original monolithic command).
    """
    start_time = time.time()

    try:
        logger.info(f"Starting podcast RENDER for episode: {input_data.episode_id}")

        # 1. Load the episode
        episode = await PodcastEpisode.get(input_data.episode_id)
        if not episode:
            raise ValueError(f"Episode '{input_data.episode_id}' not found")

        # 2. Validate state — only render drafts that are ready
        if episode.pipeline_status not in (
            PipelineStatus.DRAFT_READY.value,
            None,  # legacy episodes without pipeline_status
        ):
            raise ValueError(
                f"Episode is not ready for rendering "
                f"(current: {episode.pipeline_status})"
            )

        # 3. Episode-level TTS caching: if audio_file already exists on disk,
        #    skip re-rendering (Path B from the plan — coarse-grain cache).
        if episode.audio_file:
            from open_notebook.podcasts.audio_paths import (
                resolve_contained_audio_path,
            )

            existing = resolve_contained_audio_path(episode.audio_file)
            if existing is not None and existing.exists():
                logger.info(
                    f"Audio already exists for episode {episode.id}, "
                    f"skipping re-render: {existing}"
                )
                episode.pipeline_status = PipelineStatus.COMPLETED.value
                await episode.save()
                return RenderPodcastOutput(
                    success=True,
                    episode_id=str(episode.id),
                    audio_file_path=episode.audio_file,
                    processing_time=time.time() - start_time,
                )

        # 4. Load profiles from stored snapshots
        ep_profile_name = episode.episode_profile.get("name")
        sp_profile_name = episode.speaker_profile.get("name")
        if not ep_profile_name or not sp_profile_name:
            raise ValueError(
                "Episode is missing profile name in stored snapshot — "
                "cannot resolve profiles for rendering"
            )

        episode_profile = await EpisodeProfile.get_by_name(ep_profile_name)
        speaker_profile = await SpeakerProfile.resolve(sp_profile_name)
        if not episode_profile or not speaker_profile:
            raise ValueError("Could not resolve episode or speaker profile")

        if not speaker_profile.voice_model:
            raise ValueError(
                f"Speaker profile '{speaker_profile.name}' has no voice model."
            )

        # 5. Mark as RENDERING
        episode.pipeline_status = PipelineStatus.RENDERING.value
        await episode.save()

        # 6. Configure podcast-creator and render
        await _resolve_and_configure_podcast_creator(episode_profile, speaker_profile)

        episode_dir_name, output_dir = build_episode_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting TTS + audio concatenation...")
        result = await create_podcast(
            content=episode.content,
            briefing=episode.briefing,
            episode_name=episode_dir_name,
            output_dir=str(output_dir),
            speaker_config=speaker_profile.name,
            episode_profile=episode_profile.name,
        )

        # 7. Handle audio output
        raw_audio_path = result.get("final_output_file_path") if result else None
        audio_error: Optional[str] = None
        if raw_audio_path is not None and str(raw_audio_path).startswith("ERROR:"):
            audio_error = str(raw_audio_path)
            raw_audio_path = None

        audio_file_rel = (
            to_relative_audio_path(raw_audio_path) if raw_audio_path else None
        )
        episode.audio_file = audio_file_rel

        if audio_error:
            episode.pipeline_status = PipelineStatus.FAILED.value
            await episode.save()
            raise RuntimeError(f"Podcast audio generation failed: {audio_error}")

        # 8. Mark COMPLETED
        episode.pipeline_status = PipelineStatus.COMPLETED.value
        await episode.save()

        processing_time = time.time() - start_time
        logger.info(
            f"Render complete for episode {episode.id} in {processing_time:.2f}s"
        )

        return RenderPodcastOutput(
            success=True,
            episode_id=str(episode.id),
            audio_file_path=audio_file_rel,
            processing_time=processing_time,
        )

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Podcast render failed: {e}")
        logger.exception(e)
        # Try to mark episode as FAILED
        try:
            episode = await PodcastEpisode.get(input_data.episode_id)
            if episode:
                episode.pipeline_status = PipelineStatus.FAILED.value
                await episode.save()
        except Exception:
            pass
        raise RuntimeError(str(e)) from e


# ---------------------------------------------------------------------------
# Legacy monolithic command — kept for backward compatibility
# ---------------------------------------------------------------------------


class PodcastGenerationInput(CommandInput):
    episode_profile: str
    speaker_profile: Optional[str] = None
    episode_name: str
    content: str
    briefing_suffix: Optional[str] = None


class PodcastGenerationOutput(CommandOutput):
    success: bool
    episode_id: Optional[str] = None
    audio_file_path: Optional[str] = None
    transcript: Optional[dict] = None
    outline: Optional[dict] = None
    processing_time: float
    error_message: Optional[str] = None


@command("generate_podcast", app="open_notebook", retry={"max_attempts": 1})
async def generate_podcast_command(
    input_data: PodcastGenerationInput,
) -> PodcastGenerationOutput:
    """Legacy monolithic podcast generation — delegates to draft + render.

    Kept for backward compatibility with existing API consumers. New code
    should use draft_podcast + render_podcast separately to get the review
    gate between outline/transcript and TTS.
    """
    start_time = time.time()

    try:
        # Phase 1: Draft
        draft_result = await draft_podcast_command(
            DraftPodcastInput(
                episode_profile=input_data.episode_profile,
                speaker_profile=input_data.speaker_profile,
                episode_name=input_data.episode_name,
                content=input_data.content,
                briefing_suffix=input_data.briefing_suffix,
            )
        )

        if not draft_result.success or not draft_result.episode_id:
            raise RuntimeError("Draft phase failed — cannot proceed to render")

        # Phase 2: Render
        render_result = await render_podcast_command(
            RenderPodcastInput(episode_id=draft_result.episode_id)
        )

        processing_time = time.time() - start_time

        return PodcastGenerationOutput(
            success=render_result.success,
            episode_id=draft_result.episode_id,
            audio_file_path=render_result.audio_file_path,
            transcript=draft_result.transcript,
            outline=draft_result.outline,
            processing_time=processing_time,
            error_message=render_result.error_message,
        )

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Podcast generation failed: {e}")
        logger.exception(e)
        error_msg = str(e)
        if "Invalid json output" in error_msg or "Expecting value" in error_msg:
            error_msg += (
                "\n\nNOTE: This error commonly occurs with models that use "
                "extended thinking. Try a different model in your episode profile."
            )
        raise RuntimeError(error_msg) from e
