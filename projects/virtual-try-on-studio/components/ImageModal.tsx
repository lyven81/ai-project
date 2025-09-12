import React from 'react';
import { XIcon, DownloadIcon } from './icons';

interface ImageModalProps {
  src: string;
  pose: string;
  onClose: () => void;
}

export const ImageModal: React.FC<ImageModalProps> = ({ src, pose, onClose }) => {
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = src;
    link.download = `virtual-try-on-${pose.toLowerCase().replace(/ /g, '-')}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="image-modal-title"
    >
      <div 
        className="relative bg-white dark:bg-slate-800 rounded-lg shadow-2xl max-w-3xl w-full max-h-[90vh] flex flex-col animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-700">
          <h2 id="image-modal-title" className="text-lg font-bold text-slate-800 dark:text-slate-200">{pose}</h2>
          <button 
            onClick={onClose} 
            className="p-1 rounded-full text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
            aria-label="Close"
          >
            <XIcon className="w-6 h-6" />
          </button>
        </div>
        
        <div className="p-4 flex-grow overflow-auto">
          <img src={src} alt={`Full view of ${pose}`} className="w-full h-auto object-contain max-h-[calc(90vh-140px)]" />
        </div>
        
        <div className="p-4 border-t border-slate-200 dark:border-slate-700 flex justify-end">
          <button 
            onClick={handleDownload}
            className="flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg shadow-md hover:bg-indigo-700 transition-colors duration-200"
          >
            <DownloadIcon className="w-5 h-5" />
            <span>Download</span>
          </button>
        </div>
      </div>
    </div>
  );
};