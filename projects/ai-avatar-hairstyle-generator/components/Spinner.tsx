
import React from 'react';

interface SpinnerProps {
  message: string;
}

const Spinner: React.FC<SpinnerProps> = ({ message }) => {
  const messages = [
    "Warming up the AI stylists...",
    "Finding the perfect angles...",
    "Mixing digital hair dyes...",
    "This style is going to be amazing...",
    "Just a few more snips...",
  ];
  const [reassuringMessage, setReassuringMessage] = React.useState(messages[0]);

  React.useEffect(() => {
    const intervalId = setInterval(() => {
      setReassuringMessage(prev => {
        const currentIndex = messages.indexOf(prev);
        const nextIndex = (currentIndex + 1) % messages.length;
        return messages[nextIndex];
      });
    }, 3000);

    return () => clearInterval(intervalId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="flex flex-col items-center justify-center text-center p-8">
      <div className="w-16 h-16 border-4 border-dashed rounded-full animate-spin border-indigo-500"></div>
      <p className="mt-6 text-xl font-semibold text-gray-200">{message}</p>
      <p className="mt-2 text-gray-400">{reassuringMessage}</p>
    </div>
  );
};

export default Spinner;
