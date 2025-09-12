import React, { useState, useCallback, useEffect } from 'react';
import { UploadedFile } from '../types';
import { MAX_PEOPLE } from '../constants';
import { UserIcon, UploadIcon } from './icons/Icons';

interface ImageUploaderProps {
  onFilesChange: (files: UploadedFile[]) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onFilesChange }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    onFilesChange(files);
  }, [files, onFilesChange]);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (!selectedFiles) return;

    const newFiles: File[] = Array.from(selectedFiles);

    if (files.length + newFiles.length > MAX_PEOPLE) {
      setError(`You can only upload a maximum of ${MAX_PEOPLE} photos.`);
      return;
    }
    
    setError(null);

    const newUploadedFiles = newFiles.map(file => ({
      id: `${file.name}-${Date.now()}`,
      file,
      preview: URL.createObjectURL(file),
    }));

    setFiles(prevFiles => [...prevFiles, ...newUploadedFiles]);
  }, [files.length]);

  const removeFile = useCallback((id: string) => {
    setFiles(prevFiles => {
      const fileToRemove = prevFiles.find(f => f.id === id);
      if (fileToRemove) {
        URL.revokeObjectURL(fileToRemove.preview);
      }
      return prevFiles.filter(file => file.id !== id);
    });
    if (files.length - 1 < MAX_PEOPLE) setError(null);
  }, [files.length]);

  return (
    <div>
      <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-lg border-2 border-dashed border-gray-300 hover:border-indigo-500 transition-all duration-300 flex flex-col justify-center items-center w-full h-32 p-4 text-center">
        <UploadIcon />
        <span className="mt-2 block text-sm font-medium text-gray-600">
          Click to upload photos
        </span>
        <span className="block text-xs text-gray-500">PNG, JPG, WEBP up to 10MB</span>
        <input 
          id="file-upload" 
          name="file-upload" 
          type="file" 
          className="sr-only" 
          multiple 
          accept="image/png, image/jpeg, image/webp"
          onChange={handleFileChange}
        />
      </label>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      
      {files.length > 0 ? (
        <div className="mt-4">
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-4">
            {files.map(file => (
              <div key={file.id} className="relative group aspect-square">
                <img 
                    src={file.preview} 
                    alt={file.file.name} 
                    className="w-full h-full object-cover rounded-lg shadow-sm"
                />
                <div className="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg flex items-center justify-center">
                    <button
                        onClick={() => removeFile(file.id)}
                        className="absolute top-1 right-1 bg-red-600 text-white rounded-full p-1 leading-none"
                        aria-label="Remove image"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="mt-4 text-center text-gray-500">
            <UserIcon />
            <p>Your uploaded photos will appear here.</p>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;