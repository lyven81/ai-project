
import React from 'react';
import { COLORS } from '../constants';

interface ColorPaletteProps {
  selectedColor: string;
  onColorSelect: (color: string) => void;
  onRefresh: () => void;
  onUndo: () => void;
  canUndo: boolean;
  showRefresh: boolean;
  isLoading: boolean;
}

const RefreshIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 110 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm10 10a1 1 0 01-1-1V11.899a7.002 7.002 0 01-11.601-2.566 1 1 0 011.885-.666A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 01-1 1z" clipRule="evenodd" />
    </svg>
);

const UndoIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M11 15l-3-3m0 0l3-3m-3 3h8a5 5 0 000-10H9" />
    </svg>
);

export const ColorPalette: React.FC<ColorPaletteProps> = ({ selectedColor, onColorSelect, onRefresh, showRefresh, isLoading, onUndo, canUndo }) => {
  return (
    <div className="w-full flex flex-col gap-3 p-4 bg-white rounded-xl shadow-md border-2 border-gray-200">
      <div className="grid grid-cols-6 gap-2 w-full max-w-xs self-center">
        {COLORS.map((color) => (
          <button
            key={color}
            onClick={() => onColorSelect(color)}
            className={`w-10 h-10 rounded-full cursor-pointer transition-transform duration-150 transform hover:scale-110 border-2 ${
              selectedColor === color ? 'ring-4 ring-blue-400 ring-offset-2' : 'border-gray-300'
            } ${color === '#FFFFFF' ? 'shadow-inner' : ''}`}
            style={{ backgroundColor: color }}
            aria-label={`Select color ${color}`}
          />
        ))}
      </div>
      {showRefresh && (
        <div className="flex gap-2">
            <button
                onClick={onUndo}
                disabled={isLoading || !canUndo}
                className="flex-grow flex items-center justify-center px-4 py-3 bg-gray-500 text-white font-bold rounded-lg shadow-md hover:bg-gray-600 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed transform hover:scale-105"
            >
                <UndoIcon />
                Undo
            </button>
            <button
                onClick={onRefresh}
                disabled={isLoading}
                className="flex-grow flex items-center justify-center px-4 py-3 bg-orange-500 text-white font-bold rounded-lg shadow-md hover:bg-orange-600 transition-all duration-200 disabled:bg-gray-400 disabled:cursor-not-allowed transform hover:scale-105"
            >
                <RefreshIcon />
                Start Over
            </button>
        </div>
      )}
    </div>
  );
};
