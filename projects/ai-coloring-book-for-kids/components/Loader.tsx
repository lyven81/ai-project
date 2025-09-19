
import React from 'react';

export const Loader: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center text-center">
      <div className="w-16 h-16 border-8 border-dashed rounded-full animate-spin border-blue-500"></div>
      <p className="mt-4 text-lg font-bold text-gray-600">Drawing your picture...</p>
      <p className="text-sm text-gray-500">The AI is working its magic!</p>
    </div>
  );
};
