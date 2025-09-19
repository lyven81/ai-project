
import React from 'react';

interface ThemeControlsProps {
  theme: string;
  setTheme: (theme: string) => void;
  onGenerate: () => void;
  onNext: () => void;
  isLoading: boolean;
  showNext: boolean;
}

const MagicWandIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v1.046a1 1 0 01-1.447.894l-.866-.5a1 1 0 01-.212-1.229l.053-.092a1 1 0 011.758-.167zM17 6a1 1 0 011 1v2a1 1 0 11-2 0V7a1 1 0 011-1zm-4.788-3.232a1 1 0 010 1.414l-8 8a1 1 0 01-1.414-1.414l8-8a1 1 0 011.414 0zM4 9a1 1 0 011-1h2a1 1 0 110 2H5a1 1 0 01-1-1zm12.954 2.652a1 1 0 01-1.414 0l-1.414-1.414a1 1 0 011.414-1.414l1.414 1.414a1 1 0 010 1.414zM4.929 14.929a1 1 0 011.414-1.414l.707.707a1 1 0 01-1.414 1.414l-.707-.707z" clipRule="evenodd" />
    <path d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" />
  </svg>
);

const NextIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 1.414L10.586 9H7a1 1 0 100 2h3.586l-1.293 1.293a1 1 0 101.414 1.414l3-3a1 1 0 000-1.414z" clipRule="evenodd" />
  </svg>
);


export const ThemeControls: React.FC<ThemeControlsProps> = ({ theme, setTheme, onGenerate, onNext, isLoading, showNext }) => {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      onGenerate();
    }
  };

  return (
    <div className="w-full flex flex-col gap-3 p-4 bg-white rounded-xl shadow-md border-2 border-gray-200">
      <input
        type="text"
        value={theme}
        onChange={(e) => setTheme(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="e.g., dinosaurs, space cats"
        disabled={isLoading}
        className="w-full px-4 py-2 text-lg border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-shadow"
      />
      <div className="flex gap-2">
      <button
        onClick={onGenerate}
        disabled={isLoading || !theme}
        className="flex-grow flex items-center justify-center px-4 py-3 bg-blue-500 text-white font-bold rounded-lg shadow-md hover:bg-blue-600 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed transform hover:scale-105"
      >
        <MagicWandIcon />
        Generate
      </button>
      {showNext && (
        <button
          onClick={onNext}
          disabled={isLoading}
          className="flex-grow flex items-center justify-center px-4 py-3 bg-green-500 text-white font-bold rounded-lg shadow-md hover:bg-green-600 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed transform hover:scale-105"
        >
          <NextIcon />
          Next
        </button>
      )}
      </div>
    </div>
  );
};
