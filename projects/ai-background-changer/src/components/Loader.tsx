
import React from 'react';

export const Loader: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center gap-4 text-center">
      <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-indigo-500"></div>
      <h2 className="text-xl font-semibold text-gray-200">Generating Magic...</h2>
      <p className="text-gray-400">This can take a moment. Please be patient.</p>
    </div>
  );
};
