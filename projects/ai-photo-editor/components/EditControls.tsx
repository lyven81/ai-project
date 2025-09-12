
import React from 'react';
import { MagicWandIcon } from './icons';

interface EditControlsProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
  onEdit: () => void;
  isLoading: boolean;
  hasImage: boolean;
}

export const EditControls: React.FC<EditControlsProps> = ({ prompt, setPrompt, onEdit, isLoading, hasImage }) => {
  const isDisabled = isLoading || !hasImage;

  return (
    <div className="flex flex-col space-y-4">
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="e.g., 'Add a birthday hat on the cat', 'Make the sky look like a galaxy', 'Turn this into a cartoon'"
        rows={4}
        className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-colors duration-300 disabled:opacity-50"
        disabled={!hasImage}
      />
      <button
        onClick={onEdit}
        disabled={isDisabled}
        className="w-full flex items-center justify-center px-4 py-3 font-semibold text-white bg-cyan-600 rounded-lg hover:bg-cyan-700 disabled:bg-gray-500 disabled:cursor-not-allowed transition-all duration-300 transform active:scale-95 shadow-lg"
      >
        {isLoading ? (
          <>
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Editing...
          </>
        ) : (
          <>
            <MagicWandIcon className="w-5 h-5 mr-2" />
            Generate Edit
          </>
        )}
      </button>
    </div>
  );
};
