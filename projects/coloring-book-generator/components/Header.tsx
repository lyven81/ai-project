
import React from 'react';

export const Header: React.FC = () => (
  <header className="bg-white shadow-md">
    <div className="container mx-auto px-4 md:px-8 py-4 flex items-center">
      <div className="text-3xl" role="img" aria-label="crayon">🖍️</div>
      <h1 className="text-2xl md:text-3xl font-bold text-slate-800 ml-3">
        Coloring Book <span className="text-indigo-600">Generator</span>
      </h1>
    </div>
  </header>
);
