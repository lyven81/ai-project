
import React from 'react';
import { DocumentIcon } from './icons/DocumentIcon';

interface Chapter {
  title: string;
  index: number;
}

interface TableOfContentsProps {
  chapters: Chapter[];
  currentChapterIndex: number;
  onSeek: (chapterIndex: number) => void;
}

export const TableOfContents: React.FC<TableOfContentsProps> = ({ chapters, currentChapterIndex, onSeek }) => {
  // Fix: Replace findLast with a compatible alternative to support older JS runtimes.
  const currentMainChapter = [...chapters].reverse().find(c => c.index <= currentChapterIndex);

  return (
    <div className="bg-primary p-4 rounded-lg flex-grow flex flex-col">
      <h3 className="text-lg font-semibold text-teal-accent mb-3 flex items-center">
        <DocumentIcon className="w-5 h-5 mr-2" />
        Table of Contents
      </h3>
      <nav className="flex-grow overflow-y-auto pr-2">
        <ul className="space-y-1">
          {chapters.map((chapter) => (
            <li key={chapter.index}>
              <button
                onClick={() => onSeek(chapter.index)}
                className={`w-full text-left p-2 rounded-md text-sm transition-all duration-200 ${
                  currentMainChapter?.index === chapter.index
                    ? 'bg-teal-accent text-primary font-semibold'
                    : 'text-text-dim hover:bg-accent hover:text-text-main'
                }`}
              >
                {chapter.title}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
};