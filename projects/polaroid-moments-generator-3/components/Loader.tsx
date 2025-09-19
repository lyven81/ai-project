
import React from 'react';

const loadingMessages = [
    "Mixing the pixels...",
    "Developing the film...",
    "Focusing the lens...",
    "Adjusting the aperture...",
    "Capturing the moment...",
    "Waiting for the flash..."
];

export const Loader: React.FC = () => {
    const [message, setMessage] = React.useState(loadingMessages[0]);

    React.useEffect(() => {
        const intervalId = setInterval(() => {
            setMessage(prevMessage => {
                const currentIndex = loadingMessages.indexOf(prevMessage);
                const nextIndex = (currentIndex + 1) % loadingMessages.length;
                return loadingMessages[nextIndex];
            });
        }, 2000);

        return () => clearInterval(intervalId);
    }, []);

    return (
        <div className="flex flex-col items-center justify-center my-12 text-center">
            <div className="w-12 h-12 border-4 border-t-4 border-gray-200 border-t-indigo-600 rounded-full animate-spin"></div>
            <p className="mt-4 text-lg font-semibold text-gray-700 dark:text-gray-300 transition-opacity duration-500">
                {message}
            </p>
        </div>
    );
};
