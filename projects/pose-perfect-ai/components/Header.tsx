
import React from 'react';

export const Header: React.FC = () => {
    return (
        <header className="text-center py-6 md:py-10 border-b border-gray-700/50">
            <h1 className="text-4xl md:text-5xl font-extrabold bg-gradient-to-r from-purple-400 to-indigo-500 text-transparent bg-clip-text mb-2">
                Pose Perfect AI
            </h1>
            <p className="max-w-2xl mx-auto text-gray-400">
                Transform your photos by combining a subject with a reference pose. Upload two images and let our AI create a stunning, photorealistic result.
            </p>
        </header>
    );
};
