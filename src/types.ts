export interface AppConfig {
  discord_client_id: string;
  kick_url: string;
  poll_interval: number;
  start_with_windows: boolean;
  minimize_to_tray: boolean;
  language: 'Türkçe' | 'English';
  theme: 'Dark' | 'Light';
}

export interface KickStreamData {
  is_live: boolean;
  username: string;
  channel_found: boolean;
  title: string;
  category: string;
  viewers: number;
  started_at: string | null;
  thumbnail_url: string | null;
  profile_pic?: string | null;
  url: string;
  api_status?: string;
  api_error?: string;
  error?: string;
}

export interface DiscordActivity {
  type: number;
  details?: string;
  state?: string;
  timestamps?: {
    start: number;
  };
  assets?: {
    large_image?: string;
    large_text?: string;
    small_image?: string;
    small_text?: string;
  };
  buttons?: Array<{
    label: string;
    url: string;
  }>;
}

export interface DiscordPresenceResponse {
  connected: boolean;
  client_id: string;
  activity: DiscordActivity | null;
  raw_command?: {
    cmd: string;
    args: {
      pid: number;
      activity: DiscordActivity | null;
    };
  };
}
