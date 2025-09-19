
import React, { useState, useCallback } from 'react';
import { Page, AgeGroup, DrawingStyle } from './types';
import { AGE_GROUPS, DRAWING_STYLES } from './constants';
import { generatePageIdeas, generateImage } from './services/geminiService';
import { generatePdf } from './services/pdfService';
import ControlsPanel from './components/ControlsPanel';
import PreviewArea from './components/PreviewArea';
import { Header } from './components/Header';
import { Footer } from './components/Footer';

// Define jsPDF and html2canvas on window
declare global {
  interface Window {
    jspdf: any;
    html2canvas: any;
  }
}

function App() {
  const [theme, setTheme] = useState<string>('Sea animals adventure');
  const [ageGroup, setAgeGroup] = useState<AgeGroup>(AGE_GROUPS[0]);
  const [style, setStyle] = useState<DrawingStyle>(DRAWING_STYLES[0]);
  const [pages, setPages] = useState<Page[]>([]); // Will only hold 0 or 1 page
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [pageIdeas, setPageIdeas] = useState<string[]>([]);
  const [currentPageIndex, setCurrentPageIndex] = useState<number>(0);

  const generateSinglePage = useCallback(async (idea: string, id: string) => {
    const base64Image = await generateImage(idea, ageGroup.prompt, style.prompt);
    const generatedPage: Page = {
      id: id,
      title: idea,
      imageData: base64Image,
    };
    setPages([generatedPage]);
  }, [ageGroup, style]);

  const handleGenerate = useCallback(async () => {
    if (!theme) {
      setError('Please enter a theme.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setPages([]);
    setPageIdeas([]);

    try {
      const ideas = await generatePageIdeas(theme);
      setPageIdeas(ideas);
      setCurrentPageIndex(0);
      
      if (ideas.length > 0) {
        await generateSinglePage(ideas[0], `page-0`);
      } else {
        throw new Error("No ideas were generated for this theme.");
      }
      
    } catch (err) {
      console.error(err);
      setError('Failed to generate coloring page. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [theme, generateSinglePage]);

  const handleGenerateNext = useCallback(async () => {
    if (isLoading || currentPageIndex >= pageIdeas.length - 1) {
      return;
    }
    setIsLoading(true);
    setError(null);

    const nextIndex = currentPageIndex + 1;
    try {
      await generateSinglePage(pageIdeas[nextIndex], `page-${nextIndex}`);
      setCurrentPageIndex(nextIndex);
    } catch (err) {
      console.error(err);
      setError('Failed to generate next page. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, currentPageIndex, pageIdeas, generateSinglePage]);

  const handleStartOver = () => {
    setTheme('Sea animals adventure');
    setAgeGroup(AGE_GROUPS[0]);
    setStyle(DRAWING_STYLES[0]);
    setPages([]);
    setPageIdeas([]);
    setCurrentPageIndex(0);
    setError(null);
    setIsLoading(false);
  };

  const handleDownloadPdf = async () => {
    if (pages.length === 0) return;
    setIsLoading(true);
    setError(null);
    try {
      await generatePdf(pages, theme);
    } catch (err) {
      console.error('PDF Generation Error:', err);
      setError('Could not generate PDF. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen font-sans text-slate-800">
      <Header />
      <main className="flex-grow container mx-auto p-4 md:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <div className="lg:col-span-4">
            <ControlsPanel
              theme={theme}
              setTheme={setTheme}
              ageGroup={ageGroup}
              setAgeGroup={setAgeGroup}
              style={style}
              setStyle={setStyle}
              onGenerate={handleGenerate}
              onDownload={handleDownloadPdf}
              isLoading={isLoading}
              pagesGenerated={pages.length > 0}
            />
          </div>
          <div className="lg:col-span-8">
            <PreviewArea 
              isLoading={isLoading} 
              pages={pages} 
              error={error}
              onNext={handleGenerateNext}
              onStartOver={handleStartOver}
              hasNextPage={pageIdeas.length > 0 && currentPageIndex < pageIdeas.length - 1}
            />
          </div>
        </div>
      </main>
      {pages.length > 0 && (
        <div id="print-container" className="hidden">
          {pages.map((page) => (
            <div key={page.id} id={page.id} className="bg-white p-[20mm] w-[210mm] h-[297mm] flex flex-col items-center justify-center text-center">
              <div className="w-full h-full flex flex-col">
                <h2 className="text-lg font-semibold mb-4 capitalize">{page.title}</h2>
                <div className="flex-grow w-full border-4 border-slate-400 rounded-lg flex items-center justify-center overflow-hidden p-4">
                  <img src={`data:image/png;base64,${page.imageData}`} alt={page.title} className="max-w-full max-h-full object-contain" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      <Footer />
    </div>
  );
}

export default App;
