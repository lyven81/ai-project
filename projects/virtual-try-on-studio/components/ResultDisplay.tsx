import React, { useState } from 'react';
import { CameraIcon } from './icons';
import { ImageModal } from './ImageModal';

interface ResultDisplayProps {
  images: string[];
}

const POSES = ['Front View', 'Side View', 'Back View', 'Action Pose'];

export const ResultDisplay: React.FC<ResultDisplayProps> = ({ images }) => {
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);

  const handleImageClick = (index: number) => {
    setSelectedImageIndex(index);
  };

  const handleCloseModal = () => {
    setSelectedImageIndex(null);
  };

  if (images.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full aspect-square bg-slate-100 dark:bg-slate-700/50 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-4 text-center">
        <CameraIcon className="w-16 h-16 text-slate-400 dark:text-slate-500 mb-4" />
        <h3 className="text-lg font-semibold text-slate-600 dark:text-slate-300">Your results will appear here</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Upload your photos and start the virtual try-on to see the magic happen.</p>
      </div>
    );
  }
  
  const selectedImage = selectedImageIndex !== null ? images[selectedImageIndex] : null;
  const selectedPose = selectedImageIndex !== null ? POSES[selectedImageIndex] : '';

  return (
    <>
      <div className="grid grid-cols-2 gap-4">
        {images.map((image, index) => (
          <button
            key={index}
            onClick={() => handleImageClick(index)}
            className="relative aspect-square overflow-hidden rounded-lg shadow-md border border-slate-200 dark:border-slate-700 group focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-offset-slate-800"
            aria-label={`View ${POSES[index]} in full screen`}
          >
            <img src={image} alt={`Try-on result: ${POSES[index]}`} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
            <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
              <span className="text-white font-bold text-lg">View</span>
            </div>
            <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-xs text-center p-1 font-semibold">
              {POSES[index]}
            </div>
          </button>
        ))}
      </div>
      {selectedImage && (
        <ImageModal 
          src={selectedImage}
          pose={selectedPose}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
};