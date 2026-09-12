import React, { useState } from 'react';
import { X, Copy, Check, Monitor, Terminal, FileCode2, ArrowRight } from 'lucide-react';

interface ExeGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  language: 'Türkçe' | 'English';
}

export const ExeGuideModal: React.FC<ExeGuideModalProps> = ({ isOpen, onClose, language }) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!isOpen) return null;
  const isTr = language === 'Türkçe';

  const copyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div
        className="bg-[#18181B] border border-[#303034] rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#2B2B30] bg-[#1C1C20] flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-[#53FC18]/10 text-[#53FC18]">
              <Monitor className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-[#F4F4F5]">
                {isTr ? 'KickSync.exe Nasıl Çalıştırılır / Üretilir?' : 'How to Run & Build KickSync.exe'}
              </h3>
              <p className="text-[11px] text-[#71717A]">
                {isTr ? 'Windows dosya gezgininde bu adımları izleyin' : 'Follow these steps in Windows Explorer'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-[#71717A] hover:text-[#FAFAFA] hover:bg-[#2B2B30] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-4 overflow-y-auto text-xs">
          {/* Important Info */}
          <div className="p-3.5 rounded-xl bg-[#202024] border border-[#303036] space-y-2">
            <div className="flex items-center gap-2 text-[#53FC18] font-bold text-xs">
              <FileCode2 className="w-4 h-4" />
              <span>{isTr ? 'Projede Yer Alan Windows Dosyaları:' : 'Windows Files in the Project:'}</span>
            </div>
            <ul className="space-y-1 text-[#A1A1AA] pl-5 list-disc">
              <li><code className="text-[#F4F4F5] font-mono">build_exe.bat</code>: Tek tıkla otomatik <span className="text-[#53FC18] font-bold">KickSync.exe</span> üretir.</li>
              <li><code className="text-[#F4F4F5] font-mono">run_windows.bat</code>: Derlemeden doğrudan Python ile hızlıca başlatır.</li>
              <li><code className="text-[#F4F4F5] font-mono">app/main.py</code>: OBS Kick yayınına girince Discord'u güncelleyen ana Windows kodu.</li>
            </ul>
          </div>

          {/* Step 1 */}
          <div className="space-y-1.5">
            <span className="font-bold text-[#F4F4F5] flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-[#53FC18] text-black text-[10px] flex items-center justify-center font-black">1</span>
              {isTr ? 'Projeyi Bilgisayarınıza İndirin' : 'Download the Project to your PC'}
            </span>
            <p className="text-[#A1A1AA] pl-5">
              {isTr
                ? 'Sol üst veya sağ üst menüden "Export to GitHub" veya "Download ZIP" yaparak dosyaları bilgisayarınıza indirin ve klasöre çıkartın.'
                : 'Export to GitHub or Download ZIP to your PC and extract the folder.'}
            </p>
          </div>

          {/* Step 2 */}
          <div className="space-y-1.5">
            <span className="font-bold text-[#F4F4F5] flex items-center gap-1.5">
              <span className="w-4 h-4 rounded-full bg-[#53FC18] text-black text-[10px] flex items-center justify-center font-black">2</span>
              {isTr ? 'Tek Tıkla EXE Üretin' : 'Generate EXE with 1-Click'}
            </span>
            <p className="text-[#A1A1AA] pl-5">
              {isTr
                ? 'Klasördeki ' : 'In the extracted folder, double click '}
              <strong className="text-[#53FC18]">build_exe.bat</strong>
              {isTr ? ' dosyasına çift tıklayın! Otomatik olarak ' : ' file! It will create '}
              <strong className="text-white font-mono">dist/KickSync.exe</strong>
              {isTr ? ' dosyasını oluşturup klasörü açacaktır.' : ' and open the folder.'}
            </p>
          </div>

          {/* Alternative Terminal */}
          <div className="p-3 bg-[#111113] rounded-xl border border-[#232328] space-y-1.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-[#A1A1AA] font-mono text-[10px]">
                <Terminal className="w-3.5 h-3.5 text-[#53FC18]" />
                <span>{isTr ? 'Komut İstemi / Terminal Alternatifi:' : 'Terminal Alternative:'}</span>
              </div>
              <button
                onClick={() => copyText('pip install -r requirements.txt && pyinstaller --noconsole --onefile --name "KickSync" app/main.py', 'term')}
                className="flex items-center gap-1 text-[10px] text-[#53FC18] hover:underline"
              >
                {copiedId === 'term' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                <span>{copiedId === 'term' ? (isTr ? 'Kopyalandı' : 'Copied') : (isTr ? 'Kopyala' : 'Copy')}</span>
              </button>
            </div>
            <pre className="text-[11px] font-mono text-[#53FC18] whitespace-pre-wrap select-all">
pip install -r requirements.txt
pyinstaller --noconsole --onefile --name "KickSync" app/main.py
            </pre>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-[#2B2B30] bg-[#18181B] flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-[#53FC18] hover:bg-[#68FF35] text-black text-xs font-bold rounded-lg transition-colors"
          >
            {isTr ? 'Tamam, Anladım' : 'Got It'}
          </button>
        </div>
      </div>
    </div>
  );
};
