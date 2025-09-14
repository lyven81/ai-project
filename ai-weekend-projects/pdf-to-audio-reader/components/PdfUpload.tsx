
import React, { useState, useCallback } from 'react';
import { UploadIcon } from './icons/UploadIcon';

interface PdfUploadProps {
  onFileUpload: (file: File) => void;
}

export const PdfUpload: React.FC<PdfUploadProps> = ({ onFileUpload }) => {
  const [isDragging, setIsDragging] = useState(false);

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
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        onFileUpload(file);
      }
      e.dataTransfer.clearData();
    }
  }, [onFileUpload]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileUpload(e.target.files[0]);
    }
  };

  const handleClick = () => {
    document.getElementById('pdf-upload-input')?.click();
  }

  return (
    <div className="flex-grow flex flex-col items-center justify-center text-center p-4">
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`w-full max-w-2xl p-10 border-2 border-dashed rounded-xl cursor-pointer transition-all duration-300 ${isDragging ? 'border-teal-accent bg-accent/50' : 'border-highlight hover:border-teal-accent hover:bg-accent/30'}`}
      >
        <input
          type="file"
          id="pdf-upload-input"
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />
        <div className="flex flex-col items-center">
          <UploadIcon className="w-16 h-16 text-highlight mb-4" />
          <p className="text-xl font-semibold text-text-main">Drag & Drop your PDF here</p>
          <p className="text-text-dim mt-1">or click to select a file</p>
          <p className="text-sm text-accent mt-4">Max file size: 20MB</p>
        </div>
      </div>
    </div>
  );
};
