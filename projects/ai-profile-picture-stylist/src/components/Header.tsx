import React from 'react';

export const Header: React.FC = () => {
  return (
    <header className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-10">
      <div className="container mx-auto px-4 py-4 text-center">
        <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
          AI Profile Picture Stylist
        </h1>
        <p className="mt-2 text-slate-400 max-w-2xl mx-auto">
          Upload a single photo and let AI generate four unique, professional profile pictures for you.
        </p>
      </div>
    </header>
  );
};