
import React, { useState, useCallback } from 'react';
import { ImageUploader } from './components/ImageUploader';
import { PromptInput } from './components/PromptInput';
import { GeneratedImage } from './components/GeneratedImage';
import { Loader } from './components/Loader';
import { WandIcon, ClearIcon } from './components/Icons';
import { editImageWithPrompt } from './services/geminiService';
import { fileToGenerativePart } from './utils/imageUtils';
import type { FileDetails } from './types';

const App: React.FC = () => {
  const [fileDetails, setFileDetails] = useState<FileDetails | null>(null);
  const [prompt, setPrompt] = useState<string>('');
  const [generatedImageUrl, setGeneratedImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      setFileDetails({
        file: file,
        previewUrl: reader.result as string,
      });
      setGeneratedImageUrl(null);
      setError(null);
    };
    reader.readAsDataURL(file);
  };
  
  const handleGenerate = useCallback(async () => {
    if (!fileDetails || !prompt) {
      setError('Please upload an image and enter a prompt.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedImageUrl(null);

    try {
      const imagePart = await fileToGenerativePart(fileDetails.file);
      const result = await editImageWithPrompt(imagePart, prompt);
      
      if (result) {
        setGeneratedImageUrl(result);
      } else {
        setError('Could not generate image. The model may not have returned an image.');
      }
    } catch (e) {
      console.error(e);
      setError(e instanceof Error ? e.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [fileDetails, prompt]);

  const handleClear = () => {
    setFileDetails(null);
    setPrompt('');
    setGeneratedImageUrl(null);
    setError(null);
    setIsLoading(false);
  };

  const canGenerate = fileDetails !== null && prompt.trim() !== '' && !isLoading;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-6xl">
        <header className="text-center mb-8">
          <h1 className="text-4xl sm:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-600">
            AI Background Changer
          </h1>
          <p className="mt-2 text-lg text-gray-400">
            Upload an image, describe a new background, and let AI do the magic.
          </p>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Controls */}
          <div className="bg-gray-800/50 p-6 rounded-2xl shadow-lg border border-gray-700 flex flex-col gap-6">
            <ImageUploader onImageUpload={handleImageUpload} fileDetails={fileDetails} />
            <PromptInput prompt={prompt} setPrompt={setPrompt} disabled={isLoading} />
            <div className="flex flex-col sm:flex-row gap-4 mt-2">
              <button
                onClick={handleGenerate}
                disabled={!canGenerate}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 font-semibold text-white bg-indigo-600 rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-gray-600 disabled:cursor-not-allowed transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-indigo-500"
              >
                <WandIcon />
                {isLoading ? 'Generating...' : 'Generate'}
              </button>
              <button
                onClick={handleClear}
                className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 font-semibold text-gray-300 bg-gray-700 rounded-lg hover:bg-gray-600 transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-gray-500"
              >
                <ClearIcon />
                Clear
              </button>
            </div>
          </div>

          {/* Right Column: Output */}
          <div className="bg-gray-800/50 p-6 rounded-2xl shadow-lg border border-gray-700 flex items-center justify-center min-h-[400px] lg:min-h-0">
            {isLoading ? (
              <Loader />
            ) : error ? (
              <div className="text-center text-red-400">
                <p className="font-bold">An error occurred</p>
                <p className="text-sm">{error}</p>
              </div>
            ) : (
              <GeneratedImage imageUrl={generatedImageUrl} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
