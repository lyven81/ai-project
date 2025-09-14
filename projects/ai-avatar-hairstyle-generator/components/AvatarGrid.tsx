
import React from 'react';

interface AvatarGridProps {
  avatars: string[];
}

const DownloadIcon: React.FC<{className?: string}> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
);

const AvatarCard: React.FC<{ avatarSrc: string, index: number }> = ({ avatarSrc, index }) => {
    const handleDownload = () => {
        const link = document.createElement('a');
        link.href = avatarSrc;
        link.download = `avatar-hairstyle-${index + 1}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="relative group aspect-square overflow-hidden rounded-xl shadow-lg transition-all duration-300 hover:scale-105 hover:shadow-indigo-500/30">
            <img src={avatarSrc} alt={`Generated Avatar ${index + 1}`} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <button 
                    onClick={handleDownload}
                    className="flex items-center gap-2 bg-indigo-600/80 text-white py-2 px-4 rounded-lg hover:bg-indigo-600 backdrop-blur-sm transition-all"
                    aria-label={`Download avatar ${index + 1}`}
                >
                    <DownloadIcon className="w-5 h-5" />
                    <span>Download</span>
                </button>
            </div>
        </div>
    );
};

const AvatarGrid: React.FC<AvatarGridProps> = ({ avatars }) => {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 md:gap-6">
      {avatars.map((avatar, index) => (
        <AvatarCard key={index} avatarSrc={avatar} index={index} />
      ))}
    </div>
  );
};

export default AvatarGrid;
