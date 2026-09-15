import React from 'react';

interface StatCardProps {
  id?: string;
  label: string;
  value: string;
}

export const StatCard: React.FC<StatCardProps> = ({ id, label, value }) => {
  return (
    <div
      id={id}
      className="bg-[#1B1B1F] border border-[#303034] rounded-[10px] h-[64px] px-3.5 py-2 flex flex-col justify-center transition-colors"
    >
      <span className="text-[10px] font-bold tracking-wider text-[#71717A] uppercase leading-none mb-1">
        {label}
      </span>
      <span className="text-base font-bold text-[#FAFAFA] tracking-tight truncate">
        {value}
      </span>
    </div>
  );
};
