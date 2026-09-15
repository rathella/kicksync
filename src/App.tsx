import React, { useState, useEffect, useCallback, useRef } from 'react';
import { RefreshCw, Settings, ExternalLink, Play, Radio, Wifi, Info, MonitorDown } from 'lucide-react';
import { StatusBadge } from './components/StatusBadge';
import { StreamCard } from './components/StreamCard';
import { DiscordCard } from './components/DiscordCard';
import { SettingsModal } from './components/SettingsModal';
import { DiscordPreviewModal } from './components/DiscordPreviewModal';
import { ExeGuideModal } from './components/ExeGuideModal';
import { AppConfig, KickStreamData } from './types';

// A directly opened build (file://) needs the local server origin explicitly.
const API_BASE = window.location.protocol === 'http:' || window.location.protocol === 'https:'
  ? ''
  : 'http://localhost:3000';

function channelFromUrl(value: string): string {
  try {
    const parsed = new URL(/^https?:\/\//i.test(value) ? value : `https://${value}`);
    return parsed.pathname.split('/').filter(Boolean)[0] || 'rathellaizm';
  } catch {
    return value.replace(/[^a-zA-Z0-9_-]/g, '') || 'rathellaizm';
  }
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

export default function App() {
  const [config, setConfig] = useState<AppConfig>(DEFAULT_CONFIG);
  const [stream, setStream] = useState<KickStreamData>({
    is_live: false,
    username: "rathellaizm",
    channel_found: true,
    title: "Yayın şu anda kapalı.",
    category: "Kanal şu anda canlı değil.",
    viewers: 0,
    started_at: null,
    thumbnail_url: null,
    url: "https://kick.com/rathellaizm",
  });

  const [lastCheckTime, setLastCheckTime] = useState<string>("--:--:--");
  const [elapsedTime, setElapsedTime] = useState<string>("--:--:--");
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isDiscordPreviewOpen, setIsDiscordPreviewOpen] = useState(false);
  const [isSimulatedLive, setIsSimulatedLive] = useState(false);
  const [isExeGuideOpen, setIsExeGuideOpen] = useState(false);

  const pollTimerRef = useRef<any>(null);

  const isTr = config.language === 'Türkçe';

  // Format Elapsed Time HH:MM:SS
  const calculateElapsed = useCallback((startedAtStr: string | null) => {
    if (!startedAtStr) return "--:--:--";
    try {
      const start = new Date(startedAtStr).getTime();
      const now = Date.now();
      const diffSec = Math.max(0, Math.floor((now - start) / 1000));
      const hours = Math.floor(diffSec / 3600);
      const minutes = Math.floor((diffSec % 3600) / 60);
      const seconds = diffSec % 60;
      return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        seconds.toString().padStart(2, '0'),
      ].join(':');
    } catch {
      return "--:--:--";
    }
  }, []);

  // Update ticking timer
  useEffect(() => {
    if (!stream.is_live || !stream.started_at) {
      setElapsedTime("--:--:--");
      return;
    }

    setElapsedTime(calculateElapsed(stream.started_at));
    const timer = setInterval(() => {
      setElapsedTime(calculateElapsed(stream.started_at));
    }, 1000);

    return () => clearInterval(timer);
  }, [stream.is_live, stream.started_at, calculateElapsed]);

  // Load config on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/config`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.kick_url) {
          setConfig(data);
        }
      })
      .catch((err) => {
        console.warn('Failed to load config from server:', err);
        try {
          const saved = localStorage.getItem('kicksync-config');
          if (saved) setConfig({ ...DEFAULT_CONFIG, ...JSON.parse(saved) });
        } catch {
          // Keep defaults when local storage is unavailable or corrupt.
        }
      });
  }, []);

  // Fetch Kick stream status
  const fetchStreamData = useCallback(async (currentConfig = config) => {
    setIsRefreshing(true);
    try {
      if (isSimulatedLive) {
        // Simulation mode for testing all features
        const now = new Date();
        const startSim = new Date(now.getTime() - 45 * 60 * 1000).toISOString();
        setStream({
          is_live: true,
          username: currentConfig.kick_url.split('/').filter(Boolean).pop() || "rathellaizm",
          channel_found: true,
          title: isTr ? "VALORANT RANKED GRIND | !dc !kick" : "VALORANT RANKED GRIND | !dc !kick",
          category: "VALORANT",
          viewers: 1428,
          started_at: startSim,
          thumbnail_url: "https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=800&auto=format&fit=crop",
          url: currentConfig.kick_url,
        });
      } else {
        const res = await fetch(`${API_BASE}/api/kick/stream?url=${encodeURIComponent(currentConfig.kick_url)}`);
        const data = await res.json();
        setStream(data);
      }

      const now = new Date();
      setLastCheckTime(
        [
          now.getHours().toString().padStart(2, '0'),
          now.getMinutes().toString().padStart(2, '0'),
          now.getSeconds().toString().padStart(2, '0'),
        ].join(':')
      );
    } catch (err) {
      console.warn('Error fetching stream data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, [config, isSimulatedLive, isTr]);

  // Polling loop
  useEffect(() => {
    fetchStreamData();

    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
    }

    const intervalMs = Math.max(1, config.poll_interval) * 1000;
    pollTimerRef.current = setInterval(() => {
      fetchStreamData();
    }, intervalMs);

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, [config.poll_interval, config.kick_url, isSimulatedLive, fetchStreamData]);

  // Save config handler
  const handleSaveConfig = async (newConfig: AppConfig) => {
    try {
      const res = await fetch(`${API_BASE}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newConfig),
      });
      let data: any = null;
      try {
        data = await res.json();
      } catch {
        data = null;
      }
      if (!res.ok) {
        throw new Error(data?.error || (isTr ? 'Ayarlar kaydedilemedi.' : 'Failed to save settings.'));
      }
      const savedConfig = data.config || newConfig;
      localStorage.setItem('kicksync-config', JSON.stringify(savedConfig));
      setConfig(savedConfig);
      setStream((current) => ({
        ...current,
        username: channelFromUrl(savedConfig.kick_url),
        url: savedConfig.kick_url,
      }));
      fetchStreamData(savedConfig);
    } catch (error) {
      // The packaged desktop build has no HTTP API process; persist locally.
      if (error instanceof TypeError || (error instanceof Error && error.message === 'Failed to fetch')) {
        localStorage.setItem('kicksync-config', JSON.stringify(newConfig));
        setConfig(newConfig);
        setStream((current) => ({
          ...current,
          username: channelFromUrl(newConfig.kick_url),
          url: newConfig.kick_url,
        }));
        return;
      }
      throw error;
    }
  };

  const isDark = config.theme === 'Dark';

  return (
    <div
      className={`min-h-screen flex flex-col items-center justify-center p-3 sm:p-6 transition-colors duration-200 ${
        isDark ? 'bg-[#121214] text-[#FAFAFA]' : 'bg-[#F4F4F5] text-[#18181B]'
      }`}
    >
      {/* App Window Container matching original 500px width */}
      <main
        id="kicksync-window"
        className={`w-full max-w-[480px] rounded-2xl shadow-2xl overflow-hidden border transition-colors ${
          isDark
            ? 'bg-[#18181B] border-[#303034]'
            : 'bg-white border-[#E4E4E7]'
        }`}
      >
        {/* Header Section */}
        <div className="px-6 pt-5 pb-1 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <h1 id="app-title" className="text-2xl font-bold tracking-tight text-[#FAFAFA]">
                KickSync
              </h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#53FC18]/15 text-[#53FC18] font-bold border border-[#53FC18]/30">
                v1.0
              </span>
            </div>
            <p id="app-subtitle" className="text-[11px] text-[#71717A] mt-0.5">
              Kick → Discord Rich Presence
            </p>
          </div>

          <StatusBadge isLive={stream.is_live} language={config.language} />
        </div>

        {/* Username Handle */}
        <div className="px-6 pb-2.5">
          <span id="stream-username" className="text-xs font-semibold text-[#A1A1AA] hover:text-[#53FC18] transition-colors">
            @{stream.username}
          </span>
        </div>

        {/* Stream Card */}
        <div className="px-6">
          <StreamCard
            stream={stream}
            elapsedTime={elapsedTime}
            language={config.language}
          />
        </div>

        {/* Primary Action: Open Stream */}
        <div className="px-6 pt-3">
          <a
            id="open-stream-button"
            href={stream.url || `https://kick.com/${stream.username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="w-full h-10 rounded-[20px] bg-[#53FC18] hover:bg-[#68FF35] active:bg-[#45DB12] text-black font-bold text-xs tracking-wide flex items-center justify-center gap-2 shadow-[0_2px_10px_rgba(83,252,24,0.25)] transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            <span>{isTr ? 'Yayını Aç' : 'Open Stream'}</span>
          </a>
        </div>

        {/* Secondary Actions: Refresh & Settings */}
        <div className="px-6 pt-2 grid grid-cols-2 gap-2">
          <button
            id="manual-refresh-button"
            type="button"
            onClick={() => fetchStreamData()}
            disabled={isRefreshing}
            className="h-9 rounded-[9px] bg-[#1B1B1F] hover:bg-[#29292E] border border-[#303034] text-[#C4C4CA] text-xs font-bold flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-[#53FC18]' : ''}`} />
            <span>{isTr ? 'Şimdi Yenile' : 'Refresh Now'}</span>
          </button>

          <button
            id="open-settings-button"
            type="button"
            onClick={() => setIsSettingsOpen(true)}
            className="h-9 rounded-[9px] bg-[#1B1B1F] hover:bg-[#29292E] border border-[#303034] text-[#C4C4CA] text-xs font-bold flex items-center justify-center gap-2 transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>{isTr ? 'Settings' : 'Settings'}</span>
          </button>
        </div>

        {/* Windows .EXE Helper Button */}
        <div className="px-6 pt-2">
          <button
            id="open-exe-guide-button"
            type="button"
            onClick={() => setIsExeGuideOpen(true)}
            className="w-full h-8 rounded-[8px] bg-[#1a2517] hover:bg-[#202e1c] border border-[#53FC18]/30 text-[#53FC18] text-[11px] font-bold flex items-center justify-center gap-1.5 transition-colors"
          >
            <MonitorDown className="w-3.5 h-3.5" />
            <span>{isTr ? 'Windows .EXE Çalıştırma / Derleme Rehberi' : 'Windows .EXE Build & Run Guide'}</span>
            <span className="text-[9px] bg-[#53FC18] text-black px-1.5 py-0.5 rounded font-black leading-none">.BAT</span>
          </button>
        </div>

        {/* Last Update indicator */}
        <div className="text-center py-2">
          <span id="last-update-label" className="text-[10px] text-[#5F5F67]">
            {isTr ? `Son kontrol: ${lastCheckTime}` : `Last check: ${lastCheckTime}`}
          </span>
        </div>

        {/* Discord Card */}
        <div className="px-6 pb-4">
          <DiscordCard
            connected={true}
            onOpenPreview={() => setIsDiscordPreviewOpen(true)}
            language={config.language}
          />
        </div>

        {/* Simulation / Live Test Bar */}
        <div className="px-6 py-2.5 bg-[#141416] border-t border-[#252529] flex items-center justify-between text-[11px]">
          <div className="flex items-center gap-1.5 text-[#A1A1AA]">
            <Radio className="w-3.5 h-3.5 text-[#53FC18]" />
            <span>{isTr ? 'Test Modu (Canlı Simülasyonu):' : 'Test Mode (Simulate Live):'}</span>
          </div>
          <button
            type="button"
            onClick={() => {
              const nextState = !isSimulatedLive;
              setIsSimulatedLive(nextState);
            }}
            className={`px-2.5 py-1 rounded-md text-[10px] font-bold transition-colors ${
              isSimulatedLive
                ? 'bg-[#53FC18] text-black'
                : 'bg-[#202024] text-[#A1A1AA] hover:text-white border border-[#343438]'
            }`}
          >
            {isSimulatedLive
              ? (isTr ? 'Simülasyon Açık' : 'Simulation ON')
              : (isTr ? 'Simüle Et' : 'Simulate')}
          </button>
        </div>
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        config={config}
        onSave={handleSaveConfig}
      />

      {/* Discord Preview Modal */}
      <DiscordPreviewModal
        isOpen={isDiscordPreviewOpen}
        onClose={() => setIsDiscordPreviewOpen(false)}
        stream={stream}
        config={config}
        elapsedTime={elapsedTime}
      />

      {/* EXE Guide Modal */}
      <ExeGuideModal
        isOpen={isExeGuideOpen}
        onClose={() => setIsExeGuideOpen(false)}
        language={config.language}
      />
    </div>
  );
}
