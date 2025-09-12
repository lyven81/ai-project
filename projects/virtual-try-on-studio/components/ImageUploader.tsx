
import React, { useState, useRef } from 'react';
import { UploadIcon, XIcon } from './icons';

interface ImageUploaderProps {
  id: string;
  label: string;
  onImageUpload: (base64: string) => void;
  onRemove?: () => void;
  isRemovable?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ id, label, onImageUpload, onRemove, isRemovable }) => {
  const [preview, setPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        setPreview(base64String);
        onImageUpload(base64String);
      };
      reader.readAsDataURL(file);
    }
  };
  
  const handleRemove = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    e.preventDefault();
    setPreview(null);
    if(fileInputRef.current) {
        fileInputRef.current.value = "";
    }
    if(onRemove) {
        onRemove();
    }
  }

  return (
    <div className="relative">
      <label
        htmlFor={id}
        className="cursor-pointer w-full aspect-square bg-slate-100 dark:bg-slate-700/50 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg flex flex-col items-center justify-center text-center p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700 hover:border-indigo-500 dark:hover:border-indigo-500 transition-all duration-200 overflow-hidden group"
      >
        <input
          id={id}
          ref={fileInputRef}
          type="file"
          accept="image/png, image/jpeg, image/webp"
          className="hidden"
          onChange={handleFileChange}
        />
        {preview ? (
          <img src={preview} alt={label} className="w-full h-full object-cover" />
        ) : (
          <>
            <UploadIcon className="w-8 h-8 mb-2 text-slate-400 dark:text-slate-500 group-hover:text-indigo-500 transition-colors" />
            <span className="text-sm font-semibold">{label}</span>
          </>
        )}
      </label>
      {isRemovable && (
          <button onClick={handleRemove} className="absolute -top-2 -right-2 bg-slate-600 text-white rounded-full p-1 shadow-lg hover:bg-red-500 transition-colors">
              <XIcon className="w-4 h-4" />
          </button>
      )}
    </div>
  );
};
