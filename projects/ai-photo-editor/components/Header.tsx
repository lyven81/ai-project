
import React from 'react';
import { CameraIcon } from './icons';

export const Header: React.FC = () => {
  return (
    <header className="text-center">
      <div className="flex items-center justify-center gap-4">
        <CameraIcon className="w-12 h-12 text-cyan-400"/>
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-fuchsia-500 text-transparent bg-clip-text">
          AI Photo Editor
        </h1>
      </div>
      <p className="mt-3 text-lg text-gray-400">
        Edit your photos with the power of Gemini. Just upload, describe, and transform.
      </p>
    </header>
  );
};
