import React, { useState } from 'react';

interface DownloadButtonsProps {
  avatars: string[];
  onReset: () => void;
}

const downloadGridAsPNG = async (images: string[]): Promise<void> => {
    if (images.length !== 9) return;

    const imageLoadPromises = images.map(src => {
        return new Promise<HTMLImageElement>((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    });

    try {
        const loadedImages = await Promise.all(imageLoadPromises);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        const { width, height } = loadedImages[0];
        const gap = Math.round(width * 0.05);

        canvas.width = 3 * width + 2 * gap;
        canvas.height = 3 * height + 2 * gap;

        ctx.fillStyle = '#111827'; // bg-gray-900
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        loadedImages.forEach((img, i) => {
            const col = i % 3;
            const row = Math.floor(i / 3);
            const x = col * (width + gap);
            const y = row * (height + gap);
            ctx.drawImage(img, x, y, width, height);
        });

        const dataUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = 'avatar-expression-grid.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error("Failed to create and download image grid:", error);
        alert("Could not download the grid. Please try downloading images individually.");
    }
};


const DownloadButtons: React.FC<DownloadButtonsProps> = ({ avatars, onReset }) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownloadGrid = async () => {
    setIsDownloading(true);
    await downloadGridAsPNG(avatars);
    setIsDownloading(false);
  };

  return (
    <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
      <button
        onClick={handleDownloadGrid}
        disabled={isDownloading}
        className="w-full sm:w-auto flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-800 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-all duration-300"
      >
        {isDownloading ? (
           <>
             <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
             <span>Downloading...</span>
           </>
        ) : (
          <>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.022 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            <span>Download All (Grid)</span>
          </>
        )}
      </button>
      <button
        onClick={onReset}
        className="w-full sm:w-auto bg-gray-700 hover:bg-gray-600 text-gray-200 font-bold py-3 px-6 rounded-lg transition-colors"
      >
        Start Over
      </button>
    </div>
  );
};

export default DownloadButtons;
