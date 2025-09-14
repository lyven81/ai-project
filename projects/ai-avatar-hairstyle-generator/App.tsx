
import React from 'react';
import { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import AvatarGrid from './components/AvatarGrid';
import Spinner from './components/Spinner';
import DownloadButtons from './components/DownloadButtons';
import useAvatarGenerator from './hooks/useAvatarGenerator';

const App: React.FC = () => {
  const {
    generatedAvatars,
    isLoading,
    loadingMessage,
    error,
    generateAvatars,
    reset,
  } = useAvatarGenerator();

  const handleImageUpload = (file: File) => {
    generateAvatars(file);
  };

  const handleReset = () => {
    reset();
  };
  
  const renderContent = () => {
    if (isLoading) {
      return <Spinner message={loadingMessage} />;
    }
    if (error) {
      return (
        <div className="text-center p-8 bg-red-900/20 rounded-lg">
          <p className="text-red-400 font-semibold">An Error Occurred</p>
          <p className="text-gray-300 mt-2">{error}</p>
          <button
            onClick={handleReset}
            className="mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      );
    }
    if (generatedAvatars.length > 0) {
      return (
        <>
          <AvatarGrid avatars={generatedAvatars} />
          <DownloadButtons
            avatars={generatedAvatars}
            onReset={handleReset}
          />
        </>
      );
    }
    return <FileUpload onImageUpload={handleImageUpload} />;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex flex-col items-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-5xl mx-auto">
        <Header />
        <main className="mt-8">
          {renderContent()}
        </main>
      </div>
    </div>
  );
};

export default App;
