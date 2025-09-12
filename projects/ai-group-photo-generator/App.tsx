import React, { useState, useCallback, useMemo } from 'react';
import Header from './components/Header';
import ImageUploader from './components/ImageUploader';
import PoseUploader from './components/PoseUploader';
import SceneSelector from './components/SceneSelector';
import GeneratedImage from './components/GeneratedImage';
import Footer from './components/Footer';
import { generateGroupImage } from './services/geminiService';
import { UploadedFile } from './types';
import { MIN_PEOPLE, MAX_PEOPLE } from './constants';
import AspectRatioSelector from './components/AspectRatioSelector';

type AspectRatio = '1:1' | '9:16' | '16:9';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [poseFile, setPoseFile] = useState<File | null>(null);
  const [scene, setScene] = useState<string>('');
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1');
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFilesChange = (files: UploadedFile[]) => {
    setUploadedFiles(files);
  };

  const handlePoseFileChange = (file: File | null) => {
    setPoseFile(file);
  };

  const isFormValid = useMemo(() => {
    const peopleCount = uploadedFiles.length;
    return peopleCount >= MIN_PEOPLE && peopleCount <= MAX_PEOPLE;
  }, [uploadedFiles]);

  const handleGenerateClick = useCallback(async () => {
    const peopleFiles = uploadedFiles.map(uf => uf.file);
    
    if (peopleFiles.length < MIN_PEOPLE || peopleFiles.length > MAX_PEOPLE) {
       setError(`Please provide between ${MIN_PEOPLE} and ${MAX_PEOPLE} photos of people.`);
       return;
    }
    if (!isFormValid) return;


    setIsLoading(true);
    setError(null);
    setGeneratedImage(null);

    try {
      const imageB64 = await generateGroupImage(peopleFiles, poseFile, scene, aspectRatio);
      setGeneratedImage(imageB64);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [uploadedFiles, poseFile, scene, aspectRatio, isFormValid]);
  
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          
          <div className="bg-white p-8 rounded-2xl shadow-lg space-y-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">Upload Your Photos</h2>
              <p className="text-gray-600">Add between {MIN_PEOPLE} and {MAX_PEOPLE} individual photos to get started.</p>
            </div>
            <ImageUploader onFilesChange={handleFilesChange} />
            <PoseUploader onFileChange={handlePoseFileChange} />
            <SceneSelector scene={scene} onSceneChange={setScene} />
            <AspectRatioSelector selectedRatio={aspectRatio} onRatioChange={setAspectRatio} />
            <button
              onClick={handleGenerateClick}
              disabled={!isFormValid || isLoading}
              className="w-full bg-indigo-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 flex items-center justify-center"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Generating...
                </>
              ) : 'Generate Group Photo'}
            </button>
          </div>

          <div className="bg-white p-8 rounded-2xl shadow-lg sticky top-8">
             <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">Your Generated Image</h2>
            <GeneratedImage 
              isLoading={isLoading} 
              error={error} 
              imageUrl={generatedImage} 
            />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default App;