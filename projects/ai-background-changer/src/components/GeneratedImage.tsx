
import React from 'react';
import { ImageIcon } from './Icons';

interface GeneratedImageProps {
  imageUrl: string | null;
}

export const GeneratedImage: React.FC<GeneratedImageProps> = ({ imageUrl }) => {
  if (imageUrl) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center">
        <img
          src={imageUrl}
          alt="Generated result"
          className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
        />
      </div>
    );
  }

  return (
    <div className="text-center text-gray-500">
      <ImageIcon />
      <p className="mt-4 font-semibold">Your generated image will appear here</p>
      <p className="text-sm">Get started by uploading an image and providing a prompt.</p>
    </div>
  );
};
