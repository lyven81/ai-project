
import React from 'react';

interface StyleCardProps {
  src: string;
  title: string;
  description: string;
}

export const StyleCard: React.FC<StyleCardProps> = ({ src, title, description }) => {
  return (
    <div className="bg-slate-800 rounded-xl shadow-lg overflow-hidden flex flex-col group transform transition-transform duration-300 hover:-translate-y-2">
      <div className="relative aspect-square w-full">
        {src ? (
          <img src={src} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-slate-700 flex items-center justify-center">
             <p className="text-slate-400 text-sm p-4 text-center">Image generation failed</p>
          </div>
        )}
      </div>
      <div className="p-5 flex-grow flex flex-col">
        <h3 className="text-lg font-bold text-slate-100">{title}</h3>
        <p className="mt-2 text-sm text-slate-400 flex-grow">{description}</p>
        {src && (
             <a
             href={src}
             download={`${title.toLowerCase().replace(/\s+/g, '-')}-profile.png`}
             className="mt-4 w-full text-center bg-indigo-600 text-white py-2 px-4 rounded-md text-sm font-semibold hover:bg-indigo-500 transition-colors duration-200 opacity-0 group-hover:opacity-100"
           >
             Download
           </a>
        )}
      </div>
    </div>
  );
};
