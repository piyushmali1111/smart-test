import React, { useState, useRef, useEffect } from 'react';
import { Download } from 'lucide-react';
import { cn } from '../../utils/cn';

interface DotsMenuProps {
  onExportCsv?: () => void;
  exportFilename?: string;
  className?: string;
  decorativeOnly?: boolean;
}

export const DotsMenu: React.FC<DotsMenuProps> = ({
  onExportCsv,
  exportFilename = 'data.csv',
  className,
  decorativeOnly = false,
}) => {
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [open]);

  const dotsElement = (
    <div className={cn("inline-flex items-center gap-1.5 p-1.5 rounded-md transition-colors", !decorativeOnly && "hover:bg-bg-4 cursor-pointer", className)}>
      <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_4px_rgba(34,211,238,0.5)]" />
      <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_4px_rgba(34,211,238,0.5)]" />
      <span className="w-1.5 h-1.5 rounded-full bg-accent shadow-[0_0_4px_rgba(34,211,238,0.5)]" />
    </div>
  );

  if (decorativeOnly) {
    return dotsElement;
  }

  const handleExport = () => {
    setOpen(false);
    if (onExportCsv) {
      onExportCsv();
    } else {
      const dummyCsv = "data:text/csv;charset=utf-8,metric,value\nSample,100\n";
      const encodedUri = encodeURI(dummyCsv);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", exportFilename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="relative inline-block" ref={menuRef}>
      <button
        type="button"
        aria-label="Options menu"
        onClick={() => setOpen(!open)}
        className="focus:outline-none"
      >
        {dotsElement}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1.5 z-50 min-w-[140px] rounded-panel border border-border-strong bg-bg-3 p-1.5 shadow-glow-sm backdrop-blur-md animate-in fade-in zoom-in-95 duration-150">
          <button
            type="button"
            onClick={handleExport}
            className="flex w-full items-center gap-2 rounded-btn px-3 py-2 text-xs font-medium text-text-main hover:bg-bg-4 hover:text-accent transition-colors"
          >
            <Download className="h-3.5 w-3.5 text-accent" />
            <span>Export CSV</span>
          </button>
        </div>
      )}
    </div>
  );
};
