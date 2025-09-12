
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { ImageUploader } from './components/ImageUploader';
import { ResultDisplay } from './components/ResultDisplay';
import { Footer } from './components/Footer';
import { PlusIcon, SparklesIcon } from './components/icons';
import { generateTryOnImages } from './services/geminiService';

const App: React.FC = () => {
  const [personImage, setPersonImage] = useState<string | null>(null);
  const [garmentImages, setGarmentImages] = useState<Array<string | null>>([null]);
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');

  const loadingMessages = [
    "Warming up the AI stylist...",
    "Tailoring the virtual garments...",
    "Adjusting the lighting...",
    "Checking the fit from all angles...",
    "Generating front view...",
    "Creating the perfect side profile...",
    "Capturing the back details...",
    "Simulating a natural walking pose...",
    "Finalizing the high-resolution renders...",
    "Almost ready to reveal your new look!"
  ];

  const handlePersonImageUpload = useCallback((base64: string) => {
    setPersonImage(base64);
  }, []);

  const handleGarmentImageUpload = useCallback((base64: string, index: number) => {
    setGarmentImages(prev => {
      const newGarments = [...prev];
      newGarments[index] = base64;
      return newGarments;
    });
  }, []);

  const handleAddGarmentSlot = useCallback(() => {
    setGarmentImages(prev => [...prev, null]);
  }, []);

  const handleRemoveGarmentSlot = useCallback((index: number) => {
    setGarmentImages(prev => {
      if (prev.length <= 1) return prev;
      const newGarments = [...prev];
      newGarments.splice(index, 1);
      return newGarments;
    });
  }, []);

  const handleTryOn = async () => {
    const validGarments = garmentImages.filter((img): img is string => img !== null);
    if (!personImage || validGarments.length === 0) {
      setError("Please upload a photo of a person and at least one garment.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedImages([]);

    const interval = setInterval(() => {
      setLoadingMessage(loadingMessages[Math.floor(Math.random() * loadingMessages.length)]);
    }, 2500);

    try {
      setLoadingMessage(loadingMessages[0]);
      const results = await generateTryOnImages(personImage, validGarments);
      setGeneratedImages(results);
    } catch (e) {
      console.error(e);
      setError("An error occurred while generating the try-on. Please check the console for more details.");
    } finally {
      clearInterval(interval);
      setIsLoading(false);
      setLoadingMessage('');
    }
  };

  const isTryOnDisabled = isLoading || !personImage || garmentImages.every(img => img === null);

  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-800 dark:text-slate-200">
      <Header />
      <main className="flex-grow container mx-auto p-4 md:p-8">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="flex flex-col gap-6 p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <div>
              <h2 className="text-xl font-bold text-slate-700 dark:text-slate-300 mb-2">1. Upload Your Photo</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Upload a clear, full-body photo of yourself for the best results.</p>
              <ImageUploader id="person-uploader" label="Person's Photo" onImageUpload={handlePersonImageUpload} />
            </div>

            <div>
              <h2 className="text-xl font-bold text-slate-700 dark:text-slate-300 mb-2">2. Add Clothing Items</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Add one or more garments. Use clear photos of the clothing on a plain background.</p>
              <div className="grid grid-cols-2 gap-4">
                {garmentImages.map((_, index) => (
                  <ImageUploader
                    key={index}
                    id={`garment-uploader-${index}`}
                    label={`Garment ${index + 1}`}
                    onImageUpload={(base64) => handleGarmentImageUpload(base64, index)}
                    onRemove={() => handleRemoveGarmentSlot(index)}
                    isRemovable={garmentImages.length > 1}
                  />
                ))}
                <button
                  onClick={handleAddGarmentSlot}
                  className="flex items-center justify-center w-full aspect-square bg-slate-100 dark:bg-slate-700/50 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg text-slate-400 dark:text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-700 hover:border-slate-400 dark:hover:border-slate-500 transition-colors duration-200"
                >
                  <PlusIcon className="w-8 h-8" />
                </button>
              </div>
            </div>

            <div className="mt-4">
              <button
                onClick={handleTryOn}
                disabled={isTryOnDisabled}
                className="w-full flex items-center justify-center gap-2 bg-indigo-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-slate-400 dark:disabled:bg-slate-600 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:scale-100"
              >
                {isLoading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    <span>Virtual Try-On</span>
                  </>
                )}
              </button>
              {isLoading && <p className="text-center text-sm text-indigo-500 dark:text-indigo-400 mt-3 animate-pulse">{loadingMessage}</p>}
            </div>
          </div>

          {/* Output Section */}
          <div className="p-6 bg-white dark:bg-slate-800 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
            <h2 className="text-xl font-bold text-slate-700 dark:text-slate-300 mb-4">3. Your Virtual Look</h2>
            {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg" role="alert">{error}</div>}
            <ResultDisplay images={generatedImages} />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default App;
