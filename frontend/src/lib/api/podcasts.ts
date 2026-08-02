import apiClient from './client'
import { getApiUrl } from '@/lib/config'
import {
  PodcastEpisode,
  EpisodeProfile,
  SpeakerProfile,
  Language,
  PodcastGenerationRequest,
  PodcastGenerationResponse,
  EpisodeDraft,
  BriefProposalRequest,
  BriefProposalResponse,
} from '@/lib/types/podcasts'

export type EpisodeProfileInput = Omit<EpisodeProfile, 'id'>
export type SpeakerProfileInput = Omit<SpeakerProfile, 'id'>

export async function resolvePodcastAssetUrl(path?: string | null): Promise<string | undefined> {
  if (!path) {
    return undefined
  }

  if (/^https?:\/\//i.test(path)) {
    return path
  }

  const base = await getApiUrl()

  if (path.startsWith('/')) {
    return `${base}${path}`
  }

  return `${base}/${path}`
}

export const podcastsApi = {
  listEpisodes: async () => {
    const response = await apiClient.get<PodcastEpisode[]>('/podcasts/episodes')
    return response.data
  },

  deleteEpisode: async (episodeId: string) => {
    await apiClient.delete(`/podcasts/episodes/${episodeId}`)
  },

  retryEpisode: async (episodeId: string) => {
    const response = await apiClient.post<{ job_id: string; message: string }>(
      `/podcasts/episodes/${episodeId}/retry`
    )
    return response.data
  },

  listEpisodeProfiles: async () => {
    const response = await apiClient.get<EpisodeProfile[]>('/episode-profiles')
    return response.data
  },

  createEpisodeProfile: async (payload: EpisodeProfileInput) => {
    const response = await apiClient.post<EpisodeProfile>(
      '/episode-profiles',
      payload
    )
    return response.data
  },

  updateEpisodeProfile: async (profileId: string, payload: EpisodeProfileInput) => {
    const response = await apiClient.put<EpisodeProfile>(
      `/episode-profiles/${profileId}`,
      payload
    )
    return response.data
  },

  deleteEpisodeProfile: async (profileId: string) => {
    await apiClient.delete(`/episode-profiles/${profileId}`)
  },

  duplicateEpisodeProfile: async (profileId: string) => {
    const response = await apiClient.post<EpisodeProfile>(
      `/episode-profiles/${profileId}/duplicate`
    )
    return response.data
  },

  listSpeakerProfiles: async () => {
    const response = await apiClient.get<SpeakerProfile[]>('/speaker-profiles')
    return response.data
  },

  createSpeakerProfile: async (payload: SpeakerProfileInput) => {
    const response = await apiClient.post<SpeakerProfile>(
      '/speaker-profiles',
      payload
    )
    return response.data
  },

  updateSpeakerProfile: async (profileId: string, payload: SpeakerProfileInput) => {
    const response = await apiClient.put<SpeakerProfile>(
      `/speaker-profiles/${profileId}`,
      payload
    )
    return response.data
  },

  deleteSpeakerProfile: async (profileId: string) => {
    await apiClient.delete(`/speaker-profiles/${profileId}`)
  },

  duplicateSpeakerProfile: async (profileId: string) => {
    const response = await apiClient.post<SpeakerProfile>(
      `/speaker-profiles/${profileId}/duplicate`
    )
    return response.data
  },

  generatePodcast: async (payload: PodcastGenerationRequest) => {
    const response = await apiClient.post<PodcastGenerationResponse>(
      '/podcasts/generate',
      payload
    )
    return response.data
  },

  listLanguages: async () => {
    const response = await apiClient.get<Language[]>('/languages')
    return response.data
  },

  // Draft review endpoints
  getDraft: async (episodeId: string) => {
    const response = await apiClient.get<EpisodeDraft>(
      `/podcasts/episodes/${episodeId}/draft`
    )
    return response.data
  },

  updateDraft: async (
    episodeId: string,
    payload: { transcript?: Record<string, unknown> }
  ) => {
    const response = await apiClient.patch(
      `/podcasts/episodes/${episodeId}/draft`,
      payload
    )
    return response.data
  },

  approveDraft: async (episodeId: string) => {
    const response = await apiClient.post<{
      job_id: string
      message: string
      episode_id: string
    }>(`/podcasts/episodes/${episodeId}/approve`)
    return response.data
  },

  cancelEpisode: async (episodeId: string) => {
    const response = await apiClient.post<{
      message: string
      episode_id: string
    }>(`/podcasts/episodes/${episodeId}/cancel`)
    return response.data
  },

  // Brief proposal — LLM proposes episode settings from source content
  proposeBrief: async (payload: BriefProposalRequest) => {
    const response = await apiClient.post<BriefProposalResponse>(
      '/podcasts/propose-brief',
      payload
    )
    return response.data
  },

  // Voice preview — generate a short TTS sample
  previewVoice: async (payload: {
    voice_model_id: string
    voice_id: string
    text?: string
  }): Promise<string> => {
    const response = await apiClient.post(
      '/podcasts/voices/preview',
      payload,
      { responseType: 'blob' }
    )
    return URL.createObjectURL(response.data)
  },
}
