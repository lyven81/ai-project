
import React, { useState } from 'react';
import { Difficulty } from '../types';

interface PuzzleGeneratorProps {
  onGenerate: (theme: string, difficulty: Difficulty) => void;
  error: string | null;
}

const difficultyOptions = [
  { label: "Toddler (3x3)", value: Difficulty.EASY },
  { label: "Child (4x4)", value: Difficulty.MEDIUM },
  { label: "Adult (5x5)", value: Difficulty.HARD },
];

export function PuzzleGenerator({ onGenerate, error }: PuzzleGeneratorProps) {
  const [theme, setTheme] = useState('');
  const [difficulty, setDifficulty] = useState<Difficulty>(Difficulty.EASY);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (theme.trim()) {
      onGenerate(theme.trim(), difficulty);
    }
  };

  return (
    <div className="w-full max-w-md bg-slate-800 rounded-lg shadow-xl p-8 space-y-6">
      <h2 className="text-2xl font-bold text-center text-sky-400">Create Your Puzzle</h2>
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-md text-center">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="theme" className="block text-sm font-medium text-slate-300 mb-2">
            Enter a Theme
          </label>
          <input
            id="theme"
            type="text"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="e.g., Police, Dinosaurs, Space"
            className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-md focus:ring-2 focus:ring-sky-500 focus:outline-none transition"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Select Difficulty
          </label>
          <div className="grid grid-cols-3 gap-2">
            {difficultyOptions.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setDifficulty(opt.value)}
                className={`px-4 py-2 text-sm rounded-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-sky-500 ${
                  difficulty === opt.value
                    ? 'bg-sky-600 text-white font-semibold shadow-md'
                    : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
        <button
          type="submit"
          disabled={!theme.trim()}
          className="w-full bg-emerald-600 text-white font-bold py-3 px-4 rounded-md hover:bg-emerald-500 disabled:bg-slate-600 disabled:cursor-not-allowed transition-transform transform hover:scale-105"
        >
          Generate Puzzle
        </button>
      </form>
    </div>
  );
}
