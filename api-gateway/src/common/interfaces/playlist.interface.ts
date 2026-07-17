/** TypeScript interfaces matching the Python scraper service response shapes. */

export interface IArtist {
  name: string;
  id?: string | null;
  url?: string | null;
  image_url?: string | null;
}

export interface IAlbum {
  name: string;
  id?: string | null;
  url?: string | null;
  image_url?: string | null;
  release_date?: string | null;
  total_tracks?: number | null;
}

export interface ITrack {
  title: string;
  artists: IArtist[];
  album?: IAlbum | null;
  duration_ms: number;
  duration_formatted: string;
  isrc?: string | null;
  track_number?: number | null;
  explicit: boolean;
  preview_url?: string | null;
  external_url?: string | null;
  platform_id: string;
  platform: string;
}

export interface IPlaylistInfo {
  name: string;
  description?: string | null;
  owner?: string | null;
  platform: string;
  platform_id: string;
  url: string;
  image_url?: string | null;
  total_tracks: number;
  followers?: number | null;
}

export interface IPlaylistResponse {
  success: boolean;
  platform: string;
  playlist: IPlaylistInfo;
  tracks: ITrack[];
  scraped_at: string;
  scrape_duration_ms: number;
}

export interface ISupportedPlatform {
  name: string;
  display_name: string;
  supported: boolean;
  url_patterns: string[];
}

export interface IPlatformsResponse {
  success: boolean;
  platforms: ISupportedPlatform[];
}
