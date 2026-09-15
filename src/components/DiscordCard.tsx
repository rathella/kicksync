import React from 'react';
import { ExternalLink } from 'lucide-react';

interface DiscordCardProps {
  connected: boolean;
  isLive: boolean;
  streamUrl: string;
  onOpenPreview: () => void;
  language: string;
}

export const DiscordCard: React.FC<DiscordCardProps> = ({ connected, isLive, streamUrl, onOpenPreview, language }) => {
  const isTr = language !== 'English';
  return (
    <div
      id="discord-card"
      role="button"
      tabIndex={0}
      onClick={onOpenPreview}
      onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') onOpenPreview(); }}
      className="group cursor-pointer bg-[#1B1B1F] hover:bg-[#222227] border border-[#303034] hover:border-[#45454B] rounded-[11px] min-h-[55px] px-3.5 py-2 flex items-center justify-between transition-all duration-150"
      title={isTr ? 'Discord Rich Presence onizlemesini goster' : 'Show Discord Rich Presence preview'}
    >
      <div className="flex items-center gap-2.5 min-w-0">
        <span className={`w-2.5 h-2.5 rounded-full inline-block flex-shrink-0 ${isLive ? 'bg-[#53FC18] shadow-[0_0_8px_rgba(83,252,24,0.4)]' : connected ? 'bg-[#A1A1AA]' : 'bg-[#FF707B]'}`} />
        <div className="flex items-center gap-2 min-w-0">
          <span className="text-xs font-bold text-[#E4E4E7]">Discord Rich Presence</span>
          <span className={`text-[11px] font-bold whitespace-nowrap ${isLive ? 'text-[#53FC18]' : 'text-[#A1A1AA]'}`}>
            {isLive ? (isTr ? 'Yayinda' : 'Live') : (isTr ? 'Yayin kapali' : 'Offline')}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2 text-xs text-[#71717A] group-hover:text-[#53FC18] transition-colors flex-shrink-0">
        {isLive && <a href={streamUrl} target="_blank" rel="noopener noreferrer" onClick={(event) => event.stopPropagation()} className="hidden sm:inline text-[10px] font-bold text-[#53FC18] hover:text-white">{isTr ? 'Yayini izle' : 'Watch stream'}</a>}
        <span className="text-[10px] hidden sm:inline">{isTr ? 'Onizle' : 'Preview'}</span>
        <ExternalLink className="w-3.5 h-3.5" />
      </div>
    </div>
  );
};
