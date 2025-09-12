
import React from 'react';
import { WardrobeIcon } from './icons';

export const Header: React.FC = () => {
  return (
    <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <WardrobeIcon className="w-8 h-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-slate-800 dark:text-white">
              Virtual Try-On Studio
            </h1>
          </div>
        </div>
      </div>
    </header>
  );
};
