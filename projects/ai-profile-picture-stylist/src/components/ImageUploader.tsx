
import React, { useRef, useState, useCallback } from 'react';
import { UploadIcon } from './icons/UploadIcon';

interface ImageUploaderProps {
  onImageUpload: (file: File) => void;
  imagePreviewUrl: string | null;
  isVerifying: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImageUpload, imagePreviewUrl, isVerifying }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  };

  const handleClick = () => {
    if (!isVerifying) {
        fileInputRef.current?.click();
    }
  };
  
  const handleDragEvents = useCallback((e: React.DragEvent<HTMLDivElement>, dragging: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isVerifying) {
        setIsDragging(dragging);
    }
  }, [isVerifying]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    handleDragEvents(e, false);
    if (isVerifying) return;
    const file = e.dataTransfer.files?.[0];
    if (file) {
      onImageUpload(file);
    }
  }, [handleDragEvents, onImageUpload, isVerifying]);


  return (
    <div className="w-full max-w-md">
      <div
        onClick={handleClick}
        onDragEnter={(e) => handleDragEvents(e, true)}
        onDragLeave={(e) => handleDragEvents(e, false)}
        onDragOver={(e) => handleDragEvents(e, true)}
        onDrop={handleDrop}
        className={`relative w-full aspect-square rounded-2xl border-2 border-dashed transition-all duration-300 ease-in-out group flex items-center justify-center
          ${isVerifying ? 'cursor-wait' : 'cursor-pointer'}
          ${isDragging ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-600 hover:border-indigo-500 hover:bg-slate-800/50'}
          ${imagePreviewUrl ? 'border-solid' : ''}`}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept="image/png, image/jpeg, image/webp"
          disabled={isVerifying}
        />

        {imagePreviewUrl ? (
          <>
            <img src={imagePreviewUrl} alt="Preview" className="w-full h-full object-cover rounded-2xl" />
            
            {isVerifying ? (
               <div className="absolute inset-0 bg-black/70 flex flex-col items-center justify-center transition-opacity duration-300 rounded-2xl">
                 <div className="w-8 h-8 border-2 border-dashed rounded-full animate-spin border-white"></div>
                 <span className="text-white text-sm font-semibold mt-3">Analyzing photo...</span>
              </div>
            ) : (
                <div className="absolute inset-0 bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl">
                <span className="text-white text-lg font-semibold">Change Photo</span>
                </div>
            )}
          </>
        ) : (
          <div className="text-center text-slate-400 p-8">
            <UploadIcon className={`mx-auto h-12 w-12 mb-4 transition-colors duration-300 ${isDragging ? 'text-indigo-400' : 'group-hover:text-indigo-400'}`} />
            <p className="font-semibold">
              <span className="text-indigo-400">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-slate-500 mt-2">PNG, JPG, or WEBP</p>
          </div>
        )}
      </div>
    </div>
  );
};
