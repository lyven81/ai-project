
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ImageUploader } from './components/ImageUploader';
import { EditControls } from './components/EditControls';
import { ImageDisplay } from './components/ImageDisplay';
import { Spinner } from './components/Spinner';
import { editImageWithGemini } from './services/geminiService';
import type { EditedImageResult } from './types';

const App: React.FC = () => {
  const [originalImage, setOriginalImage] = useState<string | null>(null);
  const [originalFile, setOriginalFile] = useState<File | null>(null);
  const [editedImageResult, setEditedImageResult] = useState<EditedImageResult | null>(null);
  const [prompt, setPrompt] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleImageUpload = (imageDataUrl: string, file: File) => {
    setOriginalImage(imageDataUrl);
    setOriginalFile(file);
    setEditedImageResult(null);
    setError(null);
  };

  const handleEditRequest = useCallback(async () => {
    if (!originalImage || !originalFile || !prompt.trim()) {
      setError('Please upload an image and enter an editing prompt.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setEditedImageResult(null);

    try {
      // The base64 string from FileReader includes the data URL prefix, which needs to be removed.
      const base64Data = originalImage.split(',')[1];
      const result = await editImageWithGemini(base64Data, originalFile.type, prompt);
      setEditedImageResult(result);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setIsLoading(false);
    }
  }, [originalImage, originalFile, prompt]);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-6xl mx-auto">
        <Header />
        <main className="mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4">1. Upload Photo</h2>
              <ImageUploader onImageUpload={handleImageUpload} />
            </div>
            <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4">2. Describe Edit</h2>
              <EditControls
                prompt={prompt}
                setPrompt={setPrompt}
                onEdit={handleEditRequest}
                isLoading={isLoading}
                hasImage={!!originalImage}
              />
            </div>
          </div>
          <div className="lg:col-span-8">
            <div className="bg-gray-800 p-6 rounded-2xl shadow-lg h-full">
              <h2 className="text-xl font-semibold text-cyan-400 mb-4">3. View Result</h2>
              {isLoading && <div className="w-full h-full flex items-center justify-center min-h-[400px]"><Spinner /></div>}
              {!isLoading && error && (
                <div className="flex items-center justify-center h-full bg-red-900/20 text-red-300 p-4 rounded-lg min-h-[400px]">
                  <p>{error}</p>
                </div>
              )}
              {!isLoading && !error && (
                <ImageDisplay originalImage={originalImage} editedImageResult={editedImageResult} />
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
