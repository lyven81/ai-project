
import React from 'react';

const loadingMessages = [
  "Warming up the AI's artistic circuits...",
  "Applying digital makeup and lighting...",
  "Finding your best angle in the matrix...",
  "Polishing pixels to perfection...",
  "This might take a moment, great art needs patience!",
  "Generating your new look...",
  "Finalizing your professional portraits...",
];

export const Loader: React.FC = () => {
    const [message, setMessage] = React.useState(loadingMessages[0]);
    
    React.useEffect(() => {
        const interval = setInterval(() => {
            setMessage(prevMessage => {
                const currentIndex = loadingMessages.indexOf(prevMessage);
                const nextIndex = (currentIndex + 1) % loadingMessages.length;
                return loadingMessages[nextIndex];
            });
        }, 3000);
        return () => clearInterval(interval);
    }, []);

  return (
    <div className="flex flex-col items-center justify-center text-center p-8">
      <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-indigo-400"></div>
      <h2 className="text-2xl font-semibold mt-6 text-slate-200">Generating Your Images</h2>
      <p className="text-slate-400 mt-2 transition-opacity duration-500">{message}</p>
    </div>
  );
};
