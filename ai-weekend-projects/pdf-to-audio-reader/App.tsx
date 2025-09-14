
import React, { useState, useCallback } from 'react';
import { PdfUpload } from './components/PdfUpload';
import { AudioPlayer } from './components/AudioPlayer';
import { LoadingSpinner } from './components/LoadingSpinner';
import { structurePdfText } from './services/geminiService';
import { ParsedContent } from './types';

// pdfjs-dist is loaded via CDN in index.html, so we declare the global variable.
declare const pdfjsLib: any;

const App: React.FC = () => {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [parsedContent, setParsedContent] = useState<ParsedContent[] | null>(null);
  const [sourceLanguage, setSourceLanguage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = useCallback(async (file: File) => {
    setPdfFile(file);
    setIsLoading(true);
    setError(null);
    setParsedContent(null);
    setSourceLanguage(null);

    try {
      setLoadingMessage('Reading PDF content...');
      const fileReader = new FileReader();
      fileReader.onload = async (event) => {
        if (event.target?.result) {
          try {
            const typedarray = new Uint8Array(event.target.result as ArrayBuffer);
            const pdf = await pdfjsLib.getDocument(typedarray).promise;
            let fullText = '';
            for (let i = 1; i <= pdf.numPages; i++) {
              const page = await pdf.getPage(i);
              const textContent = await page.getTextContent();
              fullText += textContent.items.map((item: any) => item.str).join(' ') + '\n';
            }
            
            setLoadingMessage('Structuring document with AI...');
            if (fullText.trim().length === 0) {
              throw new Error("This PDF appears to be empty or contains only images.");
            }
            const { structuredContent, language } = await structurePdfText(fullText);
            setParsedContent(structuredContent);
            setSourceLanguage(language);
          } catch (e: any) {
            console.error(e);
            setError(`Failed to process PDF. ${e.message}`);
          } finally {
            setIsLoading(false);
            setLoadingMessage('');
          }
        }
      };
      fileReader.readAsArrayBuffer(file);
    } catch (e: any) {
      console.error(e);
      setError('An unexpected error occurred while reading the file.');
      setIsLoading(false);
    }
  }, []);

  const handleReset = () => {
    setPdfFile(null);
    setParsedContent(null);
    setSourceLanguage(null);
    setError(null);
    setIsLoading(false);
  };

  return (
    <div className="bg-primary min-h-screen text-text-main font-sans flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-7xl mx-auto">
        <header className="text-center mb-6">
          <h1 className="text-4xl font-bold text-teal-accent">PDF-to-Audio Reader</h1>
          <p className="text-highlight mt-2">Upload a PDF and listen to it like an audiobook.</p>
        </header>
        <main className="bg-secondary rounded-lg shadow-2xl p-4 md:p-8 min-h-[70vh] flex flex-col">
          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-300 p-4 rounded-lg mb-4 text-center">
              <p><strong>Error:</strong> {error}</p>
              <button onClick={handleReset} className="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md text-white font-semibold">Try Again</button>
            </div>
          )}

          {isLoading && (
             <div className="flex flex-col items-center justify-center flex-grow">
                <LoadingSpinner />
                <p className="text-highlight mt-4 text-lg">{loadingMessage}</p>
            </div>
          )}

          {!isLoading && !parsedContent && !error && (
            <PdfUpload onFileUpload={handleFileUpload} />
          )}

          {!isLoading && parsedContent && sourceLanguage && (
            <AudioPlayer
                content={parsedContent}
                fileName={pdfFile?.name || 'Document'}
                onReset={handleReset}
                sourceLanguage={sourceLanguage}
             />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
