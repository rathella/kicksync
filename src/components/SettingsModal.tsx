import React, { useState, useEffect } from 'react';
import { X, Save, RotateCcw } from 'lucide-react';
import { AppConfig } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  config: AppConfig;
  onSave: (newConfig: AppConfig) => Promise<void>;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  config,
  onSave,
}) => {
  const [formData, setFormData] = useState<AppConfig>(config);
  const [isSaving, setIsSaving] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setFormData(config);
      setErrorMsg(null);
    }
  }, [isOpen, config]);

  if (!isOpen) return null;

  const isTr = formData.language === 'Türkçe';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.kick_url.trim()) {
      setErrorMsg(isTr ? 'Kick linki boş olamaz.' : 'Kick URL cannot be empty.');
      return;
    }
    if (isNaN(Number(formData.poll_interval)) || Number(formData.poll_interval) < 1) {
      setErrorMsg(isTr ? 'Yenileme aralığı en az 1 saniye olmalıdır.' : 'Poll interval must be at least 1 second.');
      return;
    }

    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Error saving settings');
    } finally {
      setIsSaving(false);
    }
  };

  const PRESET_STREAMERS = [
    { name: 'rathellaizm', url: 'https://kick.com/rathellaizm' },
    { name: 'xqc', url: 'https://kick.com/xqc' },
    { name: 'adinross', url: 'https://kick.com/adinross' },
    { name: 'hikaru', url: 'https://kick.com/hikaru' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="bg-[#18181B] border border-[#343438] rounded-2xl w-full max-w-[440px] shadow-2xl overflow-hidden flex flex-col max-h-[92vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 pt-6 pb-4 border-b border-[#2B2B30]">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-[#F4F4F5]">
              {isTr ? 'Settings' : 'Settings'}
            </h2>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-[#71717A] hover:text-[#FAFAFA] hover:bg-[#232326] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <p className="text-xs text-[#71717A] mt-1">
            {isTr ? 'KickSync bağlantı ve uygulama ayarları' : 'KickSync connection and application settings'}
          </p>
        </div>

        {/* Scrollable Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1 text-sm">
          {errorMsg && (
            <div className="p-2.5 rounded-lg bg-[#FF5C68]/10 border border-[#FF5C68]/30 text-[#FF5C68] text-xs font-semibold">
              {errorMsg}
            </div>
          )}

          {/* Kick URL */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-[#A1A1AA]">
              Kick URL
            </label>
            <input
              type="text"
              value={formData.kick_url}
              onChange={(e) => setFormData({ ...formData, kick_url: e.target.value })}
              placeholder="https://kick.com/kullanici"
              className="w-full px-3 py-2 bg-[#202024] border border-[#343438] focus:border-[#53FC18] focus:outline-none rounded-lg text-[#F4F4F5] text-xs transition-colors"
            />
            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[10px] text-[#71717A]">
                {isTr ? 'Hızlı Seçim:' : 'Presets:'}
              </span>
              {PRESET_STREAMERS.map((preset) => (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => setFormData({ ...formData, kick_url: preset.url })}
                  className={`text-[10px] px-2 py-0.5 rounded border transition-colors ${
                    formData.kick_url.includes(preset.name)
                      ? 'bg-[#53FC18]/15 border-[#53FC18] text-[#53FC18]'
                      : 'bg-[#202024] border-[#343438] text-[#A1A1AA] hover:border-[#53FC18]'
                  }`}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Discord Application ID */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-[#A1A1AA]">
              Discord Application ID
            </label>
            <input
              type="text"
              value={formData.discord_client_id}
              onChange={(e) => setFormData({ ...formData, discord_client_id: e.target.value })}
              placeholder="1547766245993226380"
              className="w-full px-3 py-2 bg-[#202024] border border-[#343438] focus:border-[#53FC18] focus:outline-none rounded-lg text-[#F4F4F5] text-xs font-mono transition-colors"
            />
            <p className="text-[10px] text-[#71717A]">
              {isTr
                ? 'Discord Developer Portal üzerindeki Rich Presence uygulamanızın ID’si.'
                : 'Application ID from Discord Developer Portal for Rich Presence.'}
            </p>
          </div>

          {/* Poll Interval */}
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-[#A1A1AA]">
              {isTr ? 'Yenileme aralığı (saniye)' : 'Poll Interval (seconds)'}
            </label>
            <input
              type="number"
              min="1"
              max="60"
              value={formData.poll_interval}
              onChange={(e) => setFormData({ ...formData, poll_interval: parseInt(e.target.value, 10) || 5 })}
              className="w-full px-3 py-2 bg-[#202024] border border-[#343438] focus:border-[#53FC18] focus:outline-none rounded-lg text-[#F4F4F5] text-xs transition-colors"
            />
          </div>

          {/* Switches Card */}
          <div className="bg-[#202024] border border-[#343438] rounded-xl p-3 space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-xs text-[#A1A1AA]">
                {isTr ? 'Windows açılışında başlat' : 'Start with Windows'}
              </span>
              <input
                type="checkbox"
                checked={formData.start_with_windows}
                onChange={(e) => setFormData({ ...formData, start_with_windows: e.target.checked })}
                className="w-4 h-4 accent-[#53FC18] rounded cursor-pointer"
              />
            </label>

            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-xs text-[#A1A1AA]">
                {isTr ? 'Kapatınca sistem tepsisine küçült' : 'Minimize to tray on close'}
              </span>
              <input
                type="checkbox"
                checked={formData.minimize_to_tray}
                onChange={(e) => setFormData({ ...formData, minimize_to_tray: e.target.checked })}
                className="w-4 h-4 accent-[#53FC18] rounded cursor-pointer"
              />
            </label>
          </div>

          {/* Language & Theme Selectors */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#A1A1AA]">
                {isTr ? 'Dil' : 'Language'}
              </label>
              <select
                value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value as any })}
                className="w-full px-3 py-2 bg-[#202024] border border-[#343438] focus:border-[#53FC18] focus:outline-none rounded-lg text-[#F4F4F5] text-xs cursor-pointer"
              >
                <option value="Türkçe">Türkçe</option>
                <option value="English">English</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#A1A1AA]">
                {isTr ? 'Tema' : 'Theme'}
              </label>
              <select
                value={formData.theme}
                onChange={(e) => setFormData({ ...formData, theme: e.target.value as any })}
                className="w-full px-3 py-2 bg-[#202024] border border-[#343438] focus:border-[#53FC18] focus:outline-none rounded-lg text-[#F4F4F5] text-xs cursor-pointer"
              >
                <option value="Dark">Dark</option>
                <option value="Light">Light</option>
              </select>
            </div>
          </div>
        </form>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-[#2B2B30] bg-[#18181B] flex items-center justify-end gap-2.5">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-[#232326] hover:bg-[#2C2C30] text-[#A1A1AA] hover:text-[#FAFAFA] text-xs font-semibold rounded-lg transition-colors"
          >
            {isTr ? 'İptal' : 'Cancel'}
          </button>
          <button
            type="button"
            disabled={isSaving}
            onClick={handleSubmit}
            className="px-5 py-2 bg-[#53FC18] hover:bg-[#68FF35] text-black text-xs font-bold rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? (isTr ? 'Kaydediliyor...' : 'Saving...') : (isTr ? 'Kaydet' : 'Save')}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
