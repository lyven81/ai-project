
import React from 'react';
import { Page } from '../types';
import { Loader } from './Loader';
import { NextIcon, StartOverIcon } from './icons';

interface PreviewAreaProps {
  isLoading: boolean;
  pages: Page[];
  error: string | null;
  onNext: () => void;
  onStartOver: () => void;
  hasNextPage: boolean;
}

const PreviewArea: React.FC<PreviewAreaProps> = ({ isLoading, pages, error, onNext, onStartOver, hasNextPage }) => {
  const renderContent = () => {
    if (isLoading && pages.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <Loader />
          <p className="text-slate-600 mt-4 text-lg font-medium">Generating your amazing coloring page...</p>
          <p className="text-slate-500 mt-2">This can take a moment. Please wait.</p>
        </div>
      );
    }
    
    if (error) {
      return (
        <div className="flex items-center justify-center h-full text-center text-red-600 bg-red-50 p-6 rounded-lg">
          <p className="font-semibold">{error}</p>
        </div>
      );
    }

    if (pages.length > 0) {
      const page = pages[0];
      return (
        <div className="flex flex-col h-full">
          <h2 className="text-2xl font-bold text-slate-800 mb-4 capitalize text-center">{page.title}</h2>
          <div className="flex-grow flex items-center justify-center p-4 bg-slate-100 rounded-lg">
            <img 
              src={`data:image/png;base64,${page.imageData}`} 
              alt={page.title} 
              className="max-w-full max-h-full object-contain shadow-lg rounded-md bg-white" 
            />
          </div>
          <div className="flex items-center justify-center gap-4 mt-6">
            <button
              onClick={onStartOver}
              className="flex items-center justify-center bg-slate-500 text-white font-bold py-3 px-6 rounded-lg hover:bg-slate-600 transition-all duration-300 transform hover:scale-105"
            >
              <StartOverIcon />
              <span className="ml-2">Start Over</span>
            </button>
            <button
              onClick={onNext}
              disabled={!hasNextPage || isLoading}
              className="flex items-center justify-center bg-indigo-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
            >
              <span className="mr-2">Next Page</span>
              <NextIcon />
            </button>
          </div>
          {!hasNextPage && pages.length > 0 && (
            <p className="text-center text-slate-500 mt-4">You've reached the end of this theme!</p>
          )}
        </div>
      );
    }
    
    return (
      <div className="flex flex-col items-center justify-center h-full text-center bg-slate-100 p-8 rounded-2xl border-2 border-dashed border-slate-300">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-slate-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <h3 className="text-xl font-semibold text-slate-700">Your coloring page will appear here</h3>
        <p className="text-slate-500 mt-2">Fill out the details on the left and click "Generate" to start!</p>
      </div>
    );
  };
  
  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-slate-200 min-h-[600px] h-full">
      {renderContent()}
    </div>
  );
};

export default PreviewArea;
