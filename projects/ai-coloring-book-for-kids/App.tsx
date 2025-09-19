
import React, { useState, useCallback, useRef } from 'react';
import { ColorPalette } from './components/ColorPalette';
import { ColoringCanvas, CanvasHandle } from './components/ColoringCanvas';
import { ThemeControls } from './components/ThemeControls';
import { Loader } from './components/Loader';
import { generateColoringPage } from './services/geminiService';
import { COLORS } from './constants';
import { WelcomeSplash } from './components/WelcomeSplash';

const App: React.FC = () => {
  const [theme, setTheme] = useState<string>('');
  const [activePrompt, setActivePrompt] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [selectedColor, setSelectedColor] = useState<string>(COLORS[0]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [canvasKey, setCanvasKey] = useState<number>(Date.now());
  const [canUndo, setCanUndo] = useState<boolean>(false);
  const canvasRef = useRef<CanvasHandle>(null);

  const handleGenerate = useCallback(async (currentTheme: string) => {
    if (!currentTheme || isLoading) return;

    setIsLoading(true);
    setError(null);
    setImageUrl(null);
    setCanUndo(false);

    try {
      const generatedImage = await generateColoringPage(currentTheme);
      setImageUrl(`data:image/png;base64,${generatedImage}`);
      setActivePrompt(currentTheme);
      setCanvasKey(Date.now()); // Reset canvas for the new image
    } catch (err) {
      console.error(err);
      setError('Oops! We couldn\'t create a picture. Please try another theme.');
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const handleNext = useCallback(() => {
    if (activePrompt) {
      setCanUndo(false);
      handleGenerate(activePrompt);
    }
  }, [activePrompt, handleGenerate]);

  const handleRefresh = useCallback(() => {
    setCanvasKey(Date.now());
    setCanUndo(false);
  }, []);

  const handleUndo = useCallback(() => {
    canvasRef.current?.undo();
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 text-gray-800">
      <header className="w-full max-w-5xl mb-4">
        <h1 className="text-4xl md:text-5xl font-bold text-center text-blue-600 drop-shadow-md">
          AI Coloring Book
        </h1>
        <p className="text-center text-gray-500 mt-1">What do you want to color today?</p>
      </header>

      <main className="w-full max-w-5xl flex flex-col lg:flex-row items-center lg:items-start gap-6">
        <div className="flex flex-col items-center gap-4 w-full lg:w-auto">
          <ThemeControls
            theme={theme}
            setTheme={setTheme}
            onGenerate={() => handleGenerate(theme)}
            onNext={handleNext}
            isLoading={isLoading}
            showNext={!!imageUrl}
          />
          <ColorPalette
            selectedColor={selectedColor}
            onColorSelect={setSelectedColor}
            onRefresh={handleRefresh}
            showRefresh={!!imageUrl}
            isLoading={isLoading}
            onUndo={handleUndo}
            canUndo={canUndo}
          />
        </div>
        
        <div className="flex-grow w-full h-[75vh] lg:h-auto lg:self-stretch flex items-center justify-center bg-white rounded-2xl shadow-lg border-4 border-gray-200 p-2">
          {isLoading && <Loader />}
          {error && !isLoading && (
            <div className="text-center text-red-500">
              <p className="font-bold text-xl">Error</p>
              <p>{error}</p>
            </div>
          )}
          {!isLoading && !imageUrl && !error && <WelcomeSplash />}
          {imageUrl && !isLoading && (
            <ColoringCanvas 
              ref={canvasRef}
              imageUrl={imageUrl} 
              color={selectedColor} 
              key={canvasKey} 
              onHistoryChange={setCanUndo}
            />
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
