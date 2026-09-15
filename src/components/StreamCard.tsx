import React from 'react';
import { StatCard } from './StatCard';
import { KickStreamData } from '../types';

interface StreamCardProps {
  stream: KickStreamData;
  elapsedTime: string;
  language: 'Türkçe' | 'English';
}

export const StreamCard: React.FC<StreamCardProps> = ({
  stream,
  elapsedTime,
  language,
}) => {
  const isTr = language === 'Türkçe';

  return (
    <div
      id="stream-card"
      className="bg-[#202024] border border-[#303034] rounded-[15px] overflow-hidden transition-all duration-200 shadow-lg"
    >
      {/* Thumbnail Frame */}
      <div className="relative bg-[#111113] h-[215px] m-[1px] rounded-[13px] overflow-hidden flex items-center justify-center">
        {stream.is_live && stream.thumbnail_url ? (
          <>
            <img
              src={stream.thumbnail_url}
              alt={stream.title || "Stream thumbnail"}
              className="w-full h-full object-cover"
              referrerPolicy="no-referrer"
              onError={(e) => {
                // If Kick thumbnail has expired or blocked, fallback gracefully
                (e.target as HTMLElement).style.display = 'none';
              }}
            />
            {/* Live Indicator overlay */}
            <div className="absolute top-2.5 left-2.5 bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-wide uppercase flex items-center gap-1 shadow">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              LIVE
            </div>
            {/* Viewer overlay */}
            <div className="absolute bottom-2.5 right-2.5 bg-black/80 backdrop-blur-sm text-[#FAFAFA] text-[11px] font-semibold px-2.5 py-1 rounded-md border border-white/10">
              {stream.viewers.toLocaleString()} {isTr ? 'izleyici' : 'viewers'}
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center text-center p-4">
            <span className="text-[#53FC18] font-black text-2xl tracking-widest mb-2 opacity-80">
              KICK
            </span>
            <span className="text-[#71717A] text-xs font-bold leading-tight">
              {isTr ? 'Yayın kapalı' : 'Stream Offline'}
            </span>
            {stream.api_status && (
              <span className="text-[10px] text-[#55555B] mt-1 font-mono">
                {stream.api_status}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 pt-2.5">
        <span className="text-[10px] font-bold text-[#71717A] uppercase tracking-wider block mb-0.5">
          {isTr ? 'YAYIN' : 'STREAM'}
        </span>

        {/* Title */}
        <h3
          id="stream-title"
          className="text-[15px] font-bold text-[#FAFAFA] leading-snug line-clamp-2 min-h-[42px]"
          title={stream.title || ''}
        >
          {stream.title || (isTr ? 'Yayın şu anda kapalı.' : 'Stream is currently offline.')}
        </h3>

        {/* Category */}
        <p id="stream-category" className="text-xs text-[#A1A1AA] truncate mt-1">
          {stream.category || (isTr ? 'Kanal şu anda canlı değil.' : 'Channel is not currently live.')}
        </p>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2 mt-3.5">
          <StatCard
            id="viewers-card"
            label={isTr ? 'İZLEYİCİ' : 'VIEWERS'}
            value={stream.is_live ? stream.viewers.toLocaleString() : '0'}
          />
          <StatCard
            id="elapsed-card"
            label={isTr ? 'SÜRE' : 'UPTIME'}
            value={stream.is_live ? elapsedTime : '--:--:--'}
          />
        </div>
      </div>
    </div>
  );
};
