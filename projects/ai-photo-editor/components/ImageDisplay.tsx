
import React from 'react';
import type { EditedImageResult } from '../types';
import { ImageIcon } from './icons';

interface ImageDisplayProps {
  originalImage: string | null;
  editedImageResult: EditedImageResult | null;
}

const ImageCard: React.FC<{ title: string; imageUrl: string | null; children?: React.ReactNode }> = ({ title, imageUrl, children }) => {
  return (
    <div className="flex flex-col w-full">
      <h3 className="text-lg font-medium text-center mb-2 text-gray-300">{title}</h3>
      <div className="aspect-square w-full bg-gray-700/50 rounded-lg flex items-center justify-center overflow-hidden border-2 border-gray-700">
        {imageUrl ? (
          <img src={imageUrl} alt={title} className="w-full h-full object-contain" />
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export const ImageDisplay: React.FC<ImageDisplayProps> = ({ originalImage, editedImageResult }) => {
  if (!originalImage) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-gray-500">
        <ImageIcon className="w-20 h-20 mb-4" />
        <p className="text-xl">Your images will appear here</p>
        <p>Start by uploading a photo and describing your edit.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ImageCard title="Original" imageUrl={originalImage} />
        <ImageCard title="Edited" imageUrl={editedImageResult?.image}>
            <div className="text-center text-gray-500 p-4">
                <p>Your edited image will be displayed here once generated.</p>
            </div>
        </ImageCard>
      </div>
      {editedImageResult?.text && (
        <div className="bg-gray-700/50 p-4 rounded-lg">
          <h4 className="font-semibold text-cyan-400 mb-2">AI Comments:</h4>
          <p className="text-gray-300">{editedImageResult.text}</p>
        </div>
      )}
    </div>
  );
};
