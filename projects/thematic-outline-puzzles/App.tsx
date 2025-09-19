
import React, { useState, useCallback } from 'react';
import { PuzzleGenerator } from './components/PuzzleGenerator';
import { PuzzleBoard } from './components/PuzzleBoard';
import { Spinner } from './components/Spinner';
import { generatePuzzleImage } from './services/geminiService';
import { Difficulty } from './types';
import { Logo } from './components/Logo';

type AppState = 'CONFIG' | 'LOADING' | 'PLAYING';

export default function App() {
  const [appState, setAppState] = useState<AppState>('CONFIG');
  const [puzzleImage, setPuzzleImage] = useState<string | null>(null);
  const [gridSize, setGridSize] = useState<Difficulty>(Difficulty.EASY);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<string>('');

  const handleGeneratePuzzle = useCallback(async (newTheme: string, difficulty: Difficulty) => {
    setAppState('LOADING');
    setError(null);
    setTheme(newTheme);
    setGridSize(difficulty);
    try {
      const prompt = `A vibrant and clear, minimalist outline-style, cartoon illustration of ${newTheme}. The image should be very simple, with thick, bold outlines and distinct shapes, suitable for a children's puzzle. Centered subject, plain background, square aspect ratio.`;
      const imageUrl = await generatePuzzleImage(prompt);
      setPuzzleImage(imageUrl);
      setAppState('PLAYING');
    } catch (err) {
      setError('Failed to generate image. Please try a different theme or check your API key.');
      setAppState('CONFIG');
      console.error(err);
    }
  }, []);

  const handleNewPuzzle = () => {
    setAppState('CONFIG');
    setPuzzleImage(null);
    setError(null);
  };

  const renderContent = () => {
    switch (appState) {
      case 'LOADING':
        return <Spinner message={`Creating a puzzle about "${theme}"...`} />;
      case 'PLAYING':
        if (puzzleImage) {
          return <PuzzleBoard imageSrc={puzzleImage} gridSize={gridSize} onNewPuzzle={handleNewPuzzle} theme={theme} />;
        }
        // Fallback to config if image is missing
        return <PuzzleGenerator onGenerate={handleGeneratePuzzle} error={error} />;
      case 'CONFIG':
      default:
        return <PuzzleGenerator onGenerate={handleGeneratePuzzle} error={error} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col items-center justify-center p-4 font-sans">
      <header className="w-full max-w-4xl text-center mb-8">
         <div className="flex items-center justify-center gap-4 mb-2">
            <Logo />
            <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-emerald-500">
             Thematic Outline Puzzles
            </h1>
         </div>
        <p className="text-slate-400 text-lg">Turn any theme into a fun, interactive puzzle.</p>
      </header>
      <main className="w-full flex justify-center">
        {renderContent()}
      </main>
    </div>
  );
}
