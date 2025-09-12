import React from 'react';

interface ResultDisplayProps {
    generatedImage: string | null;
}

const AwaitingIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 15v1M12 8v1M15 12h1M8 12h1" />
    </svg>
);

const DownloadIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
);


export const ResultDisplay: React.FC<ResultDisplayProps> = ({ generatedImage }) => {
    const handleDownload = () => {
        if (!generatedImage) return;
        const link = document.createElement('a');
        link.href = generatedImage;
        link.download = 'pose-perfect-result.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="flex flex-col items-center">
            <div className="w-full aspect-square bg-gray-900 rounded-lg flex items-center justify-center overflow-hidden mb-4">
                {generatedImage ? (
                    <img 
                        src={generatedImage} 
                        alt="Generated result" 
                        className="w-full h-full object-contain"
                    />
                ) : (
                    <div className="text-center text-gray-500">
                        <AwaitingIcon />
                        <p className="mt-2">Your generated image will appear here</p>
                    </div>
                )}
            </div>
            {generatedImage && (
                <button
                    onClick={handleDownload}
                    className="flex items-center justify-center px-6 py-2 font-semibold rounded-full transition-all duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-4 focus:ring-offset-2 focus:ring-offset-gray-800 bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600 shadow-lg text-white"
                >
                    <DownloadIcon />
                    Download Image
                </button>
            )}
        </div>
    );
};