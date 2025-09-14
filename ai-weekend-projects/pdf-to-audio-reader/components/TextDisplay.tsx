
import React, { useMemo } from 'react';
import { ParsedContent } from '../types';

interface TextDisplayProps {
  content: ParsedContent[];
  currentChapterIndex: number;
  currentCharIndex: number;
  playbackState: 'playing' | 'paused' | 'stopped';
}

const getContentTypeClass = (type: ParsedContent['type']): string => {
    switch(type) {
        case 'heading_1': return 'text-3xl font-bold mt-8 mb-4 text-teal-accent';
        case 'heading_2': return 'text-2xl font-semibold mt-6 mb-3 text-highlight';
        case 'image_description': return 'text-sm italic text-accent my-4 p-3 bg-primary rounded-md border-l-4 border-accent';
        case 'list_item': return 'ml-6 my-2 list-item list-disc';
        case 'paragraph':
        default: return 'text-lg leading-relaxed my-4 text-text-main';
    }
}

export const TextDisplay: React.FC<TextDisplayProps> = ({ content, currentChapterIndex, currentCharIndex, playbackState }) => {
    
    const renderedContent = useMemo(() => {
        let charCount = 0;
        let highlighted = false;

        return content.map((item, index) => {
            const itemHtml = (
                <div key={index} className={getContentTypeClass(item.type)}>
                    {item.content}
                </div>
            );

            if (playbackState !== 'playing' || index < currentChapterIndex || highlighted) {
                return itemHtml;
            }

            const chapterStartIndex = charCount;
            const chapterEndIndex = chapterStartIndex + item.content.length;
            charCount = chapterEndIndex + 1; // +1 for space between sections
            
            const totalCharsBeforeThisChapter = content.slice(0, currentChapterIndex).reduce((acc, c) => acc + c.content.length + 1, 0);
            const relativeCharIndex = currentCharIndex - totalCharsBeforeThisChapter;

            if (index === currentChapterIndex && relativeCharIndex >= 0) {
                const words = item.content.split(/(\s+)/);
                let currentWordStartIndex = 0;
                let wordFound = false;
                
                const wordSpans = words.map((word, wordIndex) => {
                    const wordEndIndex = currentWordStartIndex + word.length;
                    const isSpoken = !wordFound && relativeCharIndex >= currentWordStartIndex && relativeCharIndex < wordEndIndex;
                    if(isSpoken) wordFound = true;
                    
                    currentWordStartIndex = wordEndIndex;
                    
                    return <span key={wordIndex} className={isSpoken ? 'bg-teal-accent/40 rounded' : ''}>{word}</span>;
                });
                
                return (
                    <div key={index} className={getContentTypeClass(item.type)}>
                        {wordSpans}
                    </div>
                );
            }

            return itemHtml;
        });

    }, [content, currentChapterIndex, currentCharIndex, playbackState]);

    return <div>{renderedContent}</div>;
};
