import React, { useState, useCallback, useEffect } from 'react';
import { ImageUploader } from './components/ImageUploader';
import { ImageGrid } from './components/ImageGrid';
import { Loader } from './components/Loader';
import { generatePolaroidImages } from './services/geminiService';
import { POSE_PROMPTS } from './constants';

const App: React.FC = () => {
  const [image1, setImage1] = useState<File | null>(null);
  const [image2, setImage2] = useState<File | null>(null);
  const [image3, setImage3] = useState<File | null>(null);
  const [generatedImages, setGeneratedImages] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isApiKeyAvailable, setIsApiKeyAvailable] = useState<boolean>(false);

  useEffect(() => {
    // Proactively check for the API key on component mount
    setIsApiKeyAvailable(!!process.env.API_KEY);
  }, []);

  const handleGenerateClick = useCallback(async () => {
    if (!image1 || !image2 || !image3) {
      setError('Please upload three images to begin.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setGeneratedImages([]);

    try {
      const results = await generatePolaroidImages(image1, image2, image3, POSE_PROMPTS.map(p => p.prompt));
      setGeneratedImages(results);
    } catch (err) {
      console.error(err);
      let errorMessage = 'An unknown error occurred while generating images.';
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'object' && err !== null) {
          const errorString = JSON.stringify(err);
          if (errorString.includes('Internal error encountered')) {
              errorMessage = 'The image generation service failed. This is often caused by a missing or invalid API key in the deployment environment. Please ensure the API key is configured correctly.';
          } else if (errorString.includes('API key not valid')) {
              errorMessage = 'The provided API key is not valid. Please check your configuration.';
          } else {
              errorMessage = `An unexpected error occurred: ${errorString}`;
          }
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [image1, image2, image3]);
  
  const SparklesIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M10 3a1 1 0 011 1v2.586l1.293-1.293a1 1 0 111.414 1.414L12.414 8H15a1 1 0 110 2h-2.586l1.293 1.293a1 1 0 11-1.414 1.414L11 10.414V13a1 1 0 11-2 0v-2.586l-1.293 1.293a1 1 0 11-1.414-1.414L7.586 10H5a1 1 0 110-2h2.586L6.293 6.707a1 1 0 011.414-1.414L9 6.586V4a1 1 0 011-1zM3 3a1 1 0 011-1h1a1 1 0 110 2H4a1 1 0 01-1-1zm14 0a1 1 0 00-1 1v1a1 1 0 102 0V4a1 1 0 00-1-1zM4 15a1 1 0 100 2h1a1 1 0 100-2H4zm12 0a1 1 0 100 2h1a1 1 0 100-2h-1z" clipRule="evenodd" />
    </svg>
  );

  const WarningIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-3 text-amber-500" viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.21 3.03-1.742 3.03H4.42c-1.532 0-2.492-1.696-1.742-3.03l5.58-9.92zM10 13a1 1 0 110-2 1 1 0 010 2zm-1-4a1 1 0 011-1h.01a1 1 0 110 2H10a1 1 0 01-1-1z" clipRule="evenodd" />
    </svg>
  );

  return (
    <div className="min-h-screen text-gray-800 dark:text-gray-200 py-10 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-10">
          <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-2">
            Polaroid Moments Generator
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Create candid, retro-style photos from three images.
          </p>
        </header>

        <main>
          {!isApiKeyAvailable && (
            <div className="bg-amber-100 dark:bg-amber-900/50 border-l-4 border-amber-500 text-amber-800 dark:text-amber-200 p-4 rounded-md shadow-md mb-8 flex items-center" role="alert">
              <WarningIcon />
              <div>
                <p className="font-bold">Configuration Required</p>
                <p>The Gemini API key is not configured. Image generation is disabled. Please set the API_KEY environment variable in your deployment environment.</p>
              </div>
            </div>
          )}

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 sm:p-8 mb-8">
            <h2 className="text-2xl font-semibold mb-2 text-gray-900 dark:text-white">1. Upload Your Photos</h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Select three photos featuring the people you want in the final image.</p>
            <ImageUploader onImage1Select={setImage1} onImage2Select={setImage2} onImage3Select={setImage3} />
          </div>
          
          <div className="text-center mb-8">
            <button
              onClick={handleGenerateClick}
              disabled={!image1 || !image2 || !image3 || isLoading || !isApiKeyAvailable}
              className="inline-flex items-center justify-center bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 dark:disabled:bg-indigo-800 dark:disabled:text-gray-400 text-white font-bold py-3 px-8 rounded-full shadow-lg transform transition-all duration-300 ease-in-out hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
              title={!isApiKeyAvailable ? 'API Key is not configured. Generation is disabled.' : ''}
            >
              <SparklesIcon />
              {isLoading ? 'Generating Memories...' : 'Generate 4 Images'}
            </button>
          </div>

          {error && (
            <div className="bg-red-100 dark:bg-red-900 border-l-4 border-red-500 text-red-700 dark:text-red-200 p-4 rounded-md shadow-md" role="alert">
              <p className="font-bold">Oops! Something went wrong.</p>
              <p>{error}</p>
            </div>
          )}

          {isLoading && <Loader />}

          {!isLoading && generatedImages.length > 0 && (
            <div className="mt-12">
               <h2 className="text-2xl font-semibold mb-6 text-center text-gray-900 dark:text-white">2. Your Polaroid Moments</h2>
              <ImageGrid images={generatedImages} captions={POSE_PROMPTS.map(p => p.title)} />
            </div>
          )}
          
          {!isLoading && generatedImages.length === 0 && !error && (
            <div className="text-center text-gray-500 dark:text-gray-400 mt-12 py-8 bg-white dark:bg-gray-800/50 rounded-lg">
                <p>Your generated images will appear here.</p>
            </div>
          )}

        </main>
      </div>
    </div>
  );
};

export default App;