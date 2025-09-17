
import React, { useState, useCallback } from 'react';

interface FileUploadProps {
  onImageUpload: (file: File) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onImageUpload }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      onImageUpload(event.target.files[0]);
    }
  };

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onImageUpload(e.dataTransfer.files[0]);
    }
  }, [onImageUpload]);

  const dropzoneClasses = `
    relative flex flex-col items-center justify-center w-full max-w-xl mx-auto p-10 sm:p-16 
    border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300
    ${isDragging ? 'border-indigo-500 bg-gray-800/80 scale-105' : 'border-gray-600 hover:border-indigo-500 hover:bg-gray-800/50'}
  `;

  return (
    <div 
      className={dropzoneClasses}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={() => document.getElementById('fileInput')?.click()}
    >
      <input
        type="file"
        id="fileInput"
        className="hidden"
        accept="image/png, image/jpeg, image/webp"
        onChange={handleFileChange}
      />
      <div className="text-center">
        <svg xmlns="http://www.w3.org/2000/svg" className={`h-12 w-12 mx-auto mb-4 transition-colors ${isDragging ? 'text-indigo-400' : 'text-gray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        <p className="text-xl font-semibold text-gray-300">
          <span className="text-indigo-400">Click to upload</span> or drag and drop
        </p>
        <p className="mt-2 text-sm text-gray-500">PNG, JPG or WEBP (max 10MB)</p>
        <p className="mt-4 text-xs text-gray-500 max-w-xs mx-auto">
          For best results, use a clear photo of a person facing forward.
        </p>
      </div>
    </div>
  );
};

export default FileUpload;
