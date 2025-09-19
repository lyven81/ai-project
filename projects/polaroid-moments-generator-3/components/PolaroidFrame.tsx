import React from 'react';

interface PolaroidFrameProps {
    imageUrl: string;
    caption: string;
    rotation?: number;
}

export const PolaroidFrame: React.FC<PolaroidFrameProps> = ({ imageUrl, caption, rotation = 0 }) => {
    return (
        <div
            className="bg-white p-4 pb-14 shadow-xl rounded-sm transform transition-transform duration-300 hover:scale-105 hover:shadow-2xl relative"
            style={{ transform: `rotate(${rotation}deg)` }}
        >
            <div className="bg-gray-200 dark:bg-gray-800 aspect-square flex items-center justify-center">
                 <img src={imageUrl} alt={caption} className="object-cover w-full h-full" />
            </div>
            <p className="text-center text-lg text-gray-700 mt-4 font-mono absolute bottom-4 left-0 right-0">
                {caption}
            </p>
        </div>
    );
};