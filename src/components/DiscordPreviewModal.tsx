import React, { useState } from 'react';
import { X, Copy, Check, ExternalLink, Code } from 'lucide-react';
import { KickStreamData, AppConfig } from '../types';

interface DiscordPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  stream: KickStreamData;
  config: AppConfig;
  elapsedTime: string;
}

export const DiscordPreviewModal: React.FC<DiscordPreviewModalProps> = ({
  isOpen,
  onClose,
  stream,
  config,
  elapsedTime,
}) => {
  const [copied, setCopied] = useState(false);
  const [showJson, setShowJson] = useState(false);

  if (!isOpen) return null;

  const isTr = config.language === 'Türkçe';

  const activityPayload = {
    cmd: "SET_ACTIVITY",
    args: {
      pid: 4892,
      activity: stream.is_live ? {
        type: 0,
        name: "Kick",
        details: stream.title || (isTr ? "Canlı Yayın" : "Live Stream"),
        state: `${stream.category || "Just Chatting"} • ${stream.viewers.toLocaleString()} viewers`,
        timestamps: stream.started_at ? {
          start: Math.floor(new Date(stream.started_at).getTime() / 1000)
        } : undefined,
        assets: {
          large_image: stream.thumbnail_url || "kick_logo",
          large_text: stream.title || "Kick Stream",
          small_image: "kick_verified",
          small_text: `kick.com/${stream.username}`
        },
        buttons: [
          {
            label: isTr ? "Yayını İzle" : "Watch Stream",
            url: stream.url || `https://kick.com/${stream.username}`
          }
        ]
      } : null
    }
  };

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(activityPayload, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="bg-[#1E1F22] border border-[#313338] rounded-xl w-full max-w-md shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#2B2D31] bg-[#2B2D31]">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 fill-[#5865F2]" viewBox="0 0 127.14 96.36">
              <path d="M107.7,8.07A105.15,105.15,0,0,0,81.47,0a72.06,72.06,0,0,0-3.36,6.83A97.68,97.68,0,0,0,49,6.83,72.37,72.37,0,0,0,45.64,0,105.89,105.89,0,0,0,19.39,8.09C2.79,32.65-1.71,56.6.54,80.21h0A105.73,105.73,0,0,0,32.71,96.36,77.7,77.7,0,0,0,39.6,85.25a68.42,68.42,0,0,1-10.85-5.18c.91-.66,1.8-1.34,2.66-2a75.57,75.57,0,0,0,64.32,0c.87.71,1.76,1.39,2.66,2a68.68,68.68,0,0,1-10.87,5.19,77,77,0,0,0,6.89,11.1A105.25,105.25,0,0,0,126.6,80.22h0C129.24,52.84,122.09,29.11,107.7,8.07ZM42.45,65.69C36.18,65.69,31,60,31,53s5-12.74,11.43-12.74S54,46,53.89,53,48.84,65.69,42.45,65.69Zm42.24,0C78.41,65.69,73.25,60,73.25,53s5-12.74,11.44-12.74S96.23,46,96.12,53,91.08,65.69,84.69,65.69Z"/>
            </svg>
            <h3 className="text-sm font-semibold text-[#F2F3F5]">
              {isTr ? 'Discord Rich Presence Canlı Önizleme' : 'Discord Rich Presence Live Preview'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-[#35373C] text-[#949BA4] hover:text-[#DBDEE1] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content Body: Discord Profile Activity Mockup */}
        <div className="p-5 space-y-4">
          <div className="bg-[#111214] rounded-lg p-4 border border-[#2B2D31]">
            {/* User header in Discord */}
            <div className="flex items-center gap-3 pb-3 border-b border-[#2B2D31]">
              <div className="relative">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#5865F2] to-[#7983F5] flex items-center justify-center text-white font-bold text-sm">
                  {stream.username.charAt(0).toUpperCase()}
                </div>
                <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-[#23A55A] border-2 border-[#111214] rounded-full" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-sm font-bold text-[#F2F3F5]">{stream.username}</span>
                  <span className="text-[10px] px-1 bg-[#5865F2] text-white rounded font-bold">APP</span>
                </div>
                <div className="text-xs text-[#949BA4]">
                  {stream.is_live ? (isTr ? 'Kick Yayını Başlatıldı' : 'Streaming on Kick') : (isTr ? 'Çevrimdışı' : 'Offline')}
                </div>
              </div>
            </div>

            {/* Rich Presence Activity Box */}
            <div className="pt-3">
              <div className="text-[11px] font-bold text-[#B5BAC1] uppercase tracking-wider mb-2">
                {isTr ? 'AKTİVİTE' : 'ACTIVITY'}
              </div>

              {stream.is_live ? (
                <div className="flex items-start gap-3 bg-[#1E1F22] p-3 rounded-lg border border-[#2B2D31]">
                  {/* Large Asset with Kick icon */}
                  <div className="relative flex-shrink-0">
                    {stream.thumbnail_url ? (
                      <img
                        src={stream.thumbnail_url}
                        alt="Thumbnail"
                        className="w-16 h-16 rounded-md object-cover bg-[#2B2D31]"
                        referrerPolicy="no-referrer"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-md bg-[#000000] border border-[#53FC18]/30 flex flex-col items-center justify-center text-[#53FC18] font-black text-sm">
                        <span>KICK</span>
                        <span className="text-[9px] text-[#53FC18]/80 font-normal">LIVE</span>
                      </div>
                    )}
                    {/* Small Asset */}
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-[#53FC18] rounded-full border-2 border-[#1E1F22] flex items-center justify-center">
                      <span className="text-black font-black text-[9px]">K</span>
                    </div>
                  </div>

                  {/* Activity Details */}
                  <div className="flex-1 min-w-0">
                    <h4 className="text-xs font-bold text-[#F2F3F5] truncate leading-tight">
                      Kick
                    </h4>
                    <p className="text-xs font-semibold text-[#DBDEE1] truncate mt-0.5">
                      {stream.title || (isTr ? 'Canlı Yayın' : 'Live Stream')}
                    </p>
                    <p className="text-[11px] text-[#949BA4] truncate mt-0.5">
                      {stream.category || 'Just Chatting'} • {stream.viewers.toLocaleString()} {isTr ? 'izleyici' : 'viewers'}
                    </p>
                    <p className="text-[11px] text-[#949BA4] mt-0.5 font-mono">
                      {elapsedTime !== '--:--:--' ? `${elapsedTime} ${isTr ? 'geçti' : 'elapsed'}` : (isTr ? 'Yeni başladı' : 'Just started')}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="p-3 bg-[#1E1F22] rounded-lg border border-[#2B2D31] text-center text-xs text-[#949BA4]">
                  {isTr ? 'Yayın çevrimdışı olduğu için Discord aktivitesi şu anda temizlendi.' : 'Channel is offline. Discord activity is currently cleared.'}
                </div>
              )}

              {/* Action Button */}
              {stream.is_live && (
                <a
                  href={stream.url || `https://kick.com/${stream.username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2.5 w-full flex items-center justify-center gap-1.5 py-2 px-3 bg-[#4E5058]/40 hover:bg-[#4E5058]/70 text-[#F2F3F5] text-xs font-medium rounded transition-colors"
                >
                  <span>{isTr ? 'Yayını İzle' : 'Watch Stream'}</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#949BA4]" />
                </a>
              )}
            </div>
          </div>

          {/* Collapsible IPC Command Payload */}
          <div className="border border-[#2B2D31] rounded-lg overflow-hidden bg-[#111214]">
            <button
              onClick={() => setShowJson(!showJson)}
              className="w-full flex items-center justify-between p-3 text-left hover:bg-[#1E1F22] transition-colors"
            >
              <div className="flex items-center gap-2 text-xs font-semibold text-[#B5BAC1]">
                <Code className="w-4 h-4 text-[#5865F2]" />
                <span>Discord IPC Payload ({activityPayload.cmd})</span>
              </div>
              <span className="text-[11px] text-[#949BA4]">
                {showJson ? (isTr ? 'Gizle' : 'Hide') : (isTr ? 'Göster' : 'Show')}
              </span>
            </button>

            {showJson && (
              <div className="p-3 border-t border-[#2B2D31] bg-[#0c0d0e]">
                <div className="flex justify-end mb-1.5">
                  <button
                    onClick={handleCopyJson}
                    className="flex items-center gap-1 text-[11px] text-[#53FC18] hover:underline"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    <span>{copied ? (isTr ? 'Kopyalandı' : 'Copied') : (isTr ? 'JSON Kopyala' : 'Copy JSON')}</span>
                  </button>
                </div>
                <pre className="text-[11px] font-mono text-[#DBDEE1] overflow-x-auto max-h-48 p-2 bg-[#141517] rounded">
                  {JSON.stringify(activityPayload, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-[#2B2D31] bg-[#2B2D31] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#5865F2] hover:bg-[#4752C4] text-white text-xs font-semibold rounded transition-colors"
          >
            {isTr ? 'Kapat' : 'Close'}
          </button>
        </div>
      </div>
    </div>
  );
};
