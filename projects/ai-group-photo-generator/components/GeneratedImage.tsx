import React from 'react';
import { LoadingSpinner, ImageIcon, ErrorIcon } from './icons/Icons';

interface GeneratedImageProps {
  isLoading: boolean;
  error: string | null;
  imageUrl: string | null;
}

const GeneratedImage: React.FC<GeneratedImageProps> = ({ isLoading, error, imageUrl }) => {
  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex flex-col items-center justify-center text-center">
          <LoadingSpinner />
          <p className="mt-4 text-lg font-semibold text-gray-700">AI is working its magic...</p>
          <p className="text-sm text-gray-500">This can take a moment. Please wait.</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex flex-col items-center justify-center text-center text-red-600">
            <ErrorIcon />
            <p className="mt-4 text-lg font-semibold">Generation Failed</p>
            <p className="mt-1 text-sm max-w-sm">{error}</p>
        </div>
      );
    }

    if (imageUrl) {
      return (
        <img 
          src={imageUrl} 
          alt="Generated group" 
          className="w-full h-full object-contain rounded-lg shadow-lg" 
        />
      );
    }

    return (
      <div className="flex flex-col items-center justify-center text-center text-gray-500">
        <ImageIcon />
        <p className="mt-4 text-lg font-semibold">Your photo will appear here</p>
        <p className="text-sm">Upload photos and click generate.</p>
      </div>
    );
  };

  return (
    <div className="w-full aspect-square bg-gray-100 rounded-lg flex items-center justify-center p-4 border-2 border-dashed border-gray-300">
      {renderContent()}
    </div>
  );
};

export default GeneratedImage;
