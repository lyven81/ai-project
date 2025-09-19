
import React from 'react';

interface SpinnerProps {
    message?: string;
}

export function Spinner({ message = 'Loading...' }: SpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 bg-slate-800 rounded-lg shadow-xl">
      <div className="w-16 h-16 border-4 border-slate-600 border-t-sky-400 rounded-full animate-spin mb-4"></div>
      <p className="text-lg text-slate-300">{message}</p>
    </div>
  );
}
