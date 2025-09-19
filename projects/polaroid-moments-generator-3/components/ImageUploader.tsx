import React, { useState, useCallback, ChangeEvent, DragEvent } from 'react';

interface ImageUploaderProps {
    onImage1Select: (file: File | null) => void;
    onImage2Select: (file: File | null) => void;
    onImage3Select: (file: File | null) => void;
}

const UploadIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-gray-400 dark:text-gray-500 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
);

interface UploaderBoxProps {
  onImageSelect: (file: File | null) => void;
  id: string;
  label: string;
}

const UploaderBox: React.FC<UploaderBoxProps> = ({ onImageSelect, id, label }) => {
    const [preview, setPreview] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);

    const handleFileChange = (files: FileList | null) => {
        const file = files?.[0];
        if (file && file.type.startsWith('image/')) {
            onImageSelect(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setPreview(reader.result as string);
            };
            reader.readAsDataURL(file);
        } else {
            onImageSelect(null);
            setPreview(null);
        }
    };

    const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
        handleFileChange(e.target.files);
    };

    const onDrop = useCallback((e: DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        handleFileChange(e.dataTransfer.files);
    }, []);
    
    const onDragOver = (e: DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(true);
    };

    const onDragLeave = (e: DragEvent<HTMLLabelElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
    };

    const boxClasses = `relative flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-lg cursor-pointer transition-colors duration-200 ${isDragging ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/50' : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600'}`;

    return (
        <div className="w-full">
            <label
                htmlFor={id}
                className={boxClasses}
                onDrop={onDrop}
                onDragOver={onDragOver}
                onDragLeave={onDragLeave}
            >
                {preview ? (
                    <img src={preview} alt="Preview" className="object-cover w-full h-full rounded-lg" />
                ) : (
                    <div className="text-center">
                        <UploadIcon />
                        <p className="font-semibold text-sm text-gray-500 dark:text-gray-400">{label}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Click to upload or drag & drop</p>
                    </div>
                )}
                <input id={id} type="file" className="hidden" accept="image/*" onChange={onInputChange} />
            </label>
        </div>
    );
};


export const ImageUploader: React.FC<ImageUploaderProps> = ({ onImage1Select, onImage2Select, onImage3Select }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
            <UploaderBox onImageSelect={onImage1Select} id="photo-1" label="Upload First Photo" />
            <UploaderBox onImageSelect={onImage2Select} id="photo-2" label="Upload Second Photo" />
            <UploaderBox onImageSelect={onImage3Select} id="photo-3" label="Upload Third Photo" />
        </div>
    );
};