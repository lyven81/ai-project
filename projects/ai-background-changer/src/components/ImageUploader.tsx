
import React, { useCallback } from 'react';
import type { FileDetails } from '../types';
import { UploadIcon } from './Icons';

interface ImageUploaderProps {
  onImageUpload: (file: File) => void;
  fileDetails: FileDetails | null;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageUpload, fileDetails }) => {
  const onDrop = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      if(files[0].type.startsWith('image/')){
          onImageUpload(files[0]);
      }
    }
  }, [onImageUpload]);

  const onDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      onImageUpload(files[0]);
    }
  };

  const onContainerClick = () => {
    document.getElementById('file-input')?.click();
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-300 mb-2">
        1. Upload Your Image
      </label>
      <div
        onClick={onContainerClick}
        onDrop={onDrop}
        onDragOver={onDragOver}
        className="group w-full h-64 border-2 border-dashed border-gray-500 rounded-lg flex items-center justify-center text-center cursor-pointer hover:border-indigo-500 hover:bg-gray-800 transition-all duration-300 relative overflow-hidden"
      >
        <input
          type="file"
          id="file-input"
          className="hidden"
          accept="image/*"
          onChange={onFileChange}
        />
        {fileDetails ? (
          <img
            src={fileDetails.previewUrl}
            alt="Preview"
            className="w-full h-full object-contain"
          />
        ) : (
          <div className="text-gray-400 group-hover:text-indigo-400 transition-colors duration-300 flex flex-col items-center">
            <UploadIcon />
            <p className="mt-2 font-semibold">Click to upload or drag & drop</p>
            <p className="text-xs text-gray-500">PNG, JPG, WEBP, etc.</p>
          </div>
        )}
      </div>
    </div>
  );
};
