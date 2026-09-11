import React from 'react';
import { ExternalLink, Radio } from 'lucide-react';

interface DiscordCardProps {
  connected: boolean;
  onOpenPreview: () => void;
  language: 'Türkçe' | 'English';
}

export const DiscordCard: React.FC<DiscordCardProps> = ({
  connected,
  onOpenPreview,
  language,
}) => {
  return (
    <div
      id="discord-card"
      onClick={onOpenPreview}
      className="group cursor-pointer bg-[#1B1B1F] hover:bg-[#222227] border border-[#303034] hover:border-[#45454B] rounded-[11px] h-[55px] px-3.5 flex items-center justify-between transition-all duration-150"
      title={language === 'Türkçe' ? "Discord Rich Presence önizlemesini göster" : "Show Discord Rich Presence preview"}
    >
      <div className="flex items-center gap-2.5">
        <span
          className={`w-2.5 h-2.5 rounded-full inline-block ${
            connected ? 'bg-[#53FC18] shadow-[0_0_8px_rgba(83,252,24,0.4)]' : 'bg-[#FF707B]'
          }`}
        />
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-[#E4E4E7]">
            Discord Rich Presence
          </span>
          <span
            className={`text-[11px] font-bold ${
              connected ? 'text-[#53FC18]' : 'text-[#FF707B]'
            }`}
          >
            {connected
              ? language === 'Türkçe' ? 'Connected' : 'Connected'
              : language === 'Türkçe' ? 'Disconnected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-1.5 text-xs text-[#71717A] group-hover:text-[#53FC18] transition-colors">
        <span className="text-[10px] hidden sm:inline">
          {language === 'Türkçe' ? 'Önizle' : 'Preview'}
        </span>
        <ExternalLink className="w-3.5 h-3.5" />
      </div>
    </div>
  );
};
