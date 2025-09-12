import React, { useState, useCallback, useEffect } from 'react';
import { UploadIcon } from './icons/Icons';

interface PoseUploaderProps {
  onFileChange: (file: File | null) => void;
}

const PoseUploader: React.FC<PoseUploaderProps> = ({ onFileChange }) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    onFileChange(file);
    
    // Create a new preview URL when the file changes
    let newPreview: string | null = null;
    if (file) {
      newPreview = URL.createObjectURL(file);
      setPreview(newPreview);
    } else {
      setPreview(null);
    }

    // Cleanup function to revoke the object URL
    return () => {
      if (newPreview) {
        URL.revokeObjectURL(newPreview);
      }
    };
  }, [file, onFileChange]);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;

    if (selectedFile.size > 10 * 1024 * 1024) { // 10MB limit
        setError('File size cannot exceed 10MB.');
        return;
    }

    setError(null);
    setFile(selectedFile);
  }, []);

  const removeFile = useCallback(() => {
    setFile(null);
  }, []);

  return (
    <div>
       <label className="block text-lg font-bold text-gray-900 mb-2">
        Upload Pose Reference <span className="font-normal text-gray-500">(Optional)</span>
      </label>
      {preview && file ? (
        <div className="relative group w-full aspect-video">
          <img src={preview} alt={file.name} className="w-full h-full object-contain rounded-lg shadow-sm border border-gray-200" />
          <button
            onClick={removeFile}
            className="absolute top-2 right-2 bg-red-600 text-white rounded-full p-1.5 opacity-0 group-hover:opacity-100 transition-opacity focus:opacity-100 focus:outline-none leading-none"
            aria-label="Remove pose image"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
      ) : (
        <label htmlFor="pose-upload" className="relative cursor-pointer bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-indigo-500 transition-all duration-300 flex flex-col justify-center items-center w-full h-32 p-4 text-center">
            <UploadIcon />
            <span className="mt-2 block text-sm font-medium text-gray-600">
            Click to upload a pose reference
            </span>
            <span className="block text-xs text-gray-500">A single image showing the desired pose</span>
            <input 
            id="pose-upload" 
            name="pose-upload" 
            type="file" 
            className="sr-only" 
            accept="image/png, image/jpeg, image/webp"
            onChange={handleFileChange}
            />
        </label>
      )}
       {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
       <p className="mt-1 text-sm text-gray-500">Provide an image to guide the pose of the people in the final photo.</p>
    </div>
  );
};

export default PoseUploader;
