import React from 'react';

interface StatusBadgeProps {
  isLive: boolean;
  language?: 'Türkçe' | 'English';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ isLive }) => {
  return (
    <div
      id="status-badge"
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-[10px] text-xs font-bold uppercase transition-colors duration-200 ${
        isLive
          ? 'bg-[#17310F] text-[#53FC18]'
          : 'bg-[#292024] text-[#FF707B]'
      }`}
    >
      <span className={`w-2 h-2 rounded-full inline-block ${
        isLive ? 'bg-[#53FC18] animate-pulse' : 'bg-[#FF707B]'
      }`} />
      <span>{isLive ? 'LIVE' : 'OFFLINE'}</span>
    </div>
  );
};
