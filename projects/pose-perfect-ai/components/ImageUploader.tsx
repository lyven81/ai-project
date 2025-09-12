
import React from 'react';

interface ImageUploaderProps {
    id: string;
    title: string;
    description: string;
    imageUrl: string | undefined | null;
    onImageChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const UploadIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
);


export const ImageUploader: React.FC<ImageUploaderProps> = ({ id, title, description, imageUrl, onImageChange }) => {
    return (
        <div className="bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-700 h-full flex flex-col">
            <h3 className="text-xl font-bold text-gray-100 mb-1">{title}</h3>
            <p className="text-gray-400 mb-4 text-sm">{description}</p>
            <label 
                htmlFor={id} 
                className="flex-grow flex justify-center items-center flex-col w-full border-2 border-gray-600 border-dashed rounded-lg cursor-pointer bg-gray-800/50 hover:bg-gray-700/50 transition-colors duration-300"
            >
                {imageUrl ? (
                    <img src={imageUrl} alt="Preview" className="w-full h-full object-contain rounded-lg max-h-80" />
                ) : (
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                        <UploadIcon />
                        <p className="mb-2 text-sm text-gray-400"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                        <p className="text-xs text-gray-500">PNG, JPG, or WEBP</p>
                    </div>
                )}
                <input id={id} type="file" className="hidden" onChange={onImageChange} accept="image/png, image/jpeg, image/webp" />
            </label>
        </div>
    );
};
