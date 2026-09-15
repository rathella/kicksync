import express from 'express';
import path from 'path';
import fs from 'fs';
import cors from 'cors';
import { createServer as createViteServer } from 'vite';

interface AppConfig {
  discord_client_id: string;
  kick_url: string;
  poll_interval: number;
  start_with_windows: boolean;
  minimize_to_tray: boolean;
  language: string;
  theme: string;
}

const DEFAULT_CONFIG: AppConfig = {
  discord_client_id: "1547766245993226380",
  kick_url: "https://kick.com/rathellaizm",
  poll_interval: 5,
  start_with_windows: false,
  minimize_to_tray: false,
  language: "Türkçe",
  theme: "Dark",
};

const CONFIG_FILE = path.join(process.cwd(), 'config.json');

function readConfig(): AppConfig {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const data = fs.readFileSync(CONFIG_FILE, 'utf-8');
      return normalizeConfig({ ...DEFAULT_CONFIG, ...JSON.parse(data) });
    }
  } catch (err) {
    console.error('Error reading config.json:', err);
  }
  return DEFAULT_CONFIG;
}

function normalizeConfig(input: Partial<AppConfig>): AppConfig {
  const kickUrl = String(input.kick_url ?? DEFAULT_CONFIG.kick_url).trim();
  const discordId = String(input.discord_client_id ?? DEFAULT_CONFIG.discord_client_id).trim();
  const poll = Number(input.poll_interval);

  if (!/^\d{5,32}$/.test(discordId)) {
    throw new Error('Discord Application ID yalnızca 5-32 haneli rakamlardan oluşmalıdır.');
  }
  if (!Number.isFinite(poll) || poll < 1 || poll > 60) {
    throw new Error('Yenileme aralığı 1-60 saniye arasında olmalıdır.');
  }

  const username = extractUsername(kickUrl);
  if (!/^[a-zA-Z0-9_-]{1,64}$/.test(username)) {
    throw new Error('Geçerli bir Kick kanal URL\'si veya kanal adı girin.');
  }

  return {
    ...DEFAULT_CONFIG,
    ...input,
    kick_url: `https://kick.com/${username}`,
    discord_client_id: discordId,
    poll_interval: Math.round(poll),
    start_with_windows: Boolean(input.start_with_windows),
    minimize_to_tray: Boolean(input.minimize_to_tray),
    language: input.language === 'English' ? 'English' : 'Türkçe',
    theme: input.theme === 'Light' ? 'Light' : 'Dark',
  };
}

function writeConfig(config: AppConfig): void {
  try {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 4), 'utf-8');
  } catch (err) {
    console.error('Error writing config.json:', err);
  }
}

function extractUsername(url: string): string {
  try {
    const cleaned = url.trim();
    if (!cleaned) return 'rathellaizm';
    const parsed = new URL(cleaned.startsWith('http') ? cleaned : `https://${cleaned}`);
    const parts = parsed.pathname.split('/').filter(Boolean);
    return parts[0] || 'rathellaizm';
  } catch {
    return url.replace(/[^a-zA-Z0-9_-]/g, '') || 'rathellaizm';
  }
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(cors());
  app.use(express.json());

  // API Routes
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: 'KickSync' });
  });

  // GET Settings
  app.get('/api/config', (req, res) => {
    const config = readConfig();
    res.json(config);
  });

  // POST Settings
  app.post('/api/config', (req, res) => {
    try {
      const current = readConfig();
      const updated = normalizeConfig({ ...current, ...req.body });
      writeConfig(updated);
      res.json({ success: true, config: updated });
    } catch (error) {
      res.status(400).json({ success: false, error: error instanceof Error ? error.message : 'Geçersiz ayarlar.' });
    }
  });

  // Kick Stream API
  app.get('/api/kick/stream', async (req, res) => {
    const config = readConfig();
    const targetUrl = (req.query.url as string) || config.kick_url;
    const username = (req.query.username as string) || extractUsername(targetUrl);

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);

      const response = await fetch(`https://kick.com/api/v2/channels/${encodeURIComponent(username)}`, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': 'KickSync/1.0 (Windows NT 10.0; Win64; x64)',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 404) {
        return res.json({
          is_live: false,
          username,
          channel_found: false,
          error: `Kick kullanıcısı bulunamadı: ${username}`,
        });
      }

      if (!response.ok) {
        // Fallback for Cloudflare block (403) or rate limits
        return res.json({
          is_live: false,
          username,
          channel_found: true,
          status_code: response.status,
          title: "Yayın şu anda kapalı.",
          category: "Kanal şu anda canlı değil.",
          viewers: 0,
          started_at: null,
          thumbnail_url: null,
          api_status: `Kick API HTTP ${response.status}`,
          url: `https://kick.com/${username}`,
        });
      }

      const data = await response.json();
      const livestream = data.livestream;

      if (!livestream || !livestream.is_live) {
        return res.json({
          is_live: false,
          username,
          channel_found: true,
          title: "Yayın şu anda kapalı.",
          category: "Kanal şu anda canlı değil.",
          viewers: 0,
          started_at: null,
          thumbnail_url: data.user?.profile_pic || null,
          profile_pic: data.user?.profile_pic || null,
          bio: data.user?.bio || null,
          url: `https://kick.com/${username}`,
        });
      }

      let category: string | null = null;
      if (Array.isArray(livestream.categories) && livestream.categories.length > 0) {
        category = livestream.categories[0]?.name || null;
      }

      let thumbnailUrl: string | null = null;
      if (typeof livestream.thumbnail === 'string') {
        thumbnailUrl = livestream.thumbnail.trim() || null;
      } else if (livestream.thumbnail && typeof livestream.thumbnail.url === 'string') {
        thumbnailUrl = livestream.thumbnail.url.trim() || null;
      }

      return res.json({
        is_live: true,
        username,
        channel_found: true,
        title: livestream.session_title || 'Canlı Yayın',
        category: category || 'Just Chatting',
        viewers: parseInt(livestream.viewer_count || '0', 10),
        started_at: livestream.start_time || null,
        thumbnail_url: thumbnailUrl,
        profile_pic: data.user?.profile_pic || null,
        url: `https://kick.com/${username}`,
      });
    } catch (err: any) {
      console.warn(`Kick API fetch failed for ${username}:`, err.message);
      // Graceful offline stream response
      return res.json({
        is_live: false,
        username,
        channel_found: true,
        title: "Yayın şu anda kapalı.",
        category: "Kanal şu anda canlı değil.",
        viewers: 0,
        started_at: null,
        thumbnail_url: null,
        api_error: err.message,
        url: `https://kick.com/${username}`,
      });
    }
  });

  // Discord Presence payload generator
  app.get('/api/discord/presence', (req, res) => {
    const config = readConfig();
    const isLive = req.query.is_live === 'true';
    const username = (req.query.username as string) || extractUsername(config.kick_url);
    const title = (req.query.title as string) || 'Canlı Yayın';
    const category = (req.query.category as string) || 'Just Chatting';
    const viewers = parseInt((req.query.viewers as string) || '0', 10);
    const startedAt = req.query.started_at as string;

    const activity = {
      type: 0,
      details: isLive ? (title.slice(0, 128)) : undefined,
      state: isLive ? (`${category} • ${viewers.toLocaleString()} viewers`.slice(0, 128)) : undefined,
      timestamps: (isLive && startedAt) ? {
        start: Math.floor(new Date(startedAt).getTime() / 1000)
      } : undefined,
      assets: {
        large_image: isLive ? "kick_logo" : "kick_offline",
        large_text: isLive ? title : "Kick Streamer",
        small_image: isLive ? "kick_verified" : undefined,
        small_text: isLive ? `kick.com/${username}` : undefined
      },
      buttons: isLive ? [
        { label: config.language === 'English' ? 'Watch Stream' : 'Yayını İzle', url: `https://kick.com/${username}` }
      ] : undefined
    };

    res.json({
      connected: true,
      client_id: config.discord_client_id,
      activity: isLive ? activity : null,
      raw_command: {
        cmd: "SET_ACTIVITY",
        args: {
          pid: 1234,
          activity: isLive ? activity : null,
        }
      }
    });
  });

  // Vite middleware in dev or static files in production
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`KickSync server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
