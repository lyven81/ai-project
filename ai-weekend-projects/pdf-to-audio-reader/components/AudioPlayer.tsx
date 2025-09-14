import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ParsedContent } from '../types';
import { PlayerControls } from './PlayerControls';
import { VoiceCommander } from './VoiceCommander';
import { ChevronLeftIcon } from './icons/ChevronLeftIcon';
import { translateContent } from '../services/geminiService';
import { LoadingSpinner } from './LoadingSpinner';
import { AudioOnlyPlaceholder } from './AudioOnlyPlaceholder';

interface AudioPlayerProps {
  content: ParsedContent[];
  fileName: string;
  onReset: () => void;
  sourceLanguage: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ content, fileName, onReset, sourceLanguage }) => {
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  
  const [playbackState, setPlaybackState] = useState<'playing' | 'paused' | 'stopped'>('stopped');
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);

  const [rate, setRate] = useState(1);
  const [pitch, setPitch] = useState(1);
  
  // New states for translation
  const [displayContent, setDisplayContent] = useState<ParsedContent[]>(content);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationError, setTranslationError] = useState<string | null>(null);
  const [currentLanguage, setCurrentLanguage] = useState(sourceLanguage);

  // Translation effect
  useEffect(() => {
    if (!selectedVoice) return;

    const targetLang = selectedVoice.lang.split('-')[0];
    const sourceLang = sourceLanguage.split('-')[0];

    // Don't translate if languages are compatible (e.g., 'ms' and 'id')
    const isBahasaFamily = (lang: string) => lang === 'id' || lang === 'ms';
    if (isBahasaFamily(targetLang) && isBahasaFamily(sourceLang)) {
        if (currentLanguage !== sourceLanguage) {
            setDisplayContent(content);
            setCurrentLanguage(sourceLanguage);
            setTranslationError(null);
        }
        return;
    }

    if (targetLang !== sourceLang && currentLanguage !== selectedVoice.lang) {
        const doTranslate = async () => {
            setIsTranslating(true);
            setTranslationError(null);
            handleStop(); // Stop playback before translating
            try {
                const translated = await translateContent(content, selectedVoice.lang);
                setDisplayContent(translated);
                setCurrentLanguage(selectedVoice.lang);
            } catch (e: any) {
                setTranslationError(e.message || 'Translation failed.');
                setDisplayContent(content); // Revert to original on error
                setCurrentLanguage(sourceLanguage);
            } finally {
                setIsTranslating(false);
            }
        };
        doTranslate();
    } else if (targetLang === sourceLang && currentLanguage !== sourceLanguage) {
        // Revert to original if user selects a voice matching source lang
        setDisplayContent(content);
        setCurrentLanguage(sourceLanguage);
        setTranslationError(null);
    }
  }, [selectedVoice, content, sourceLanguage, currentLanguage]);


  const chapters = useMemo(() => {
    const result: { title: string; index: number }[] = [];
    displayContent.forEach((item, index) => {
      if (item.type === 'heading_1') {
        result.push({ title: item.content, index });
      }
    });
    // If no h1, treat every segment as a chapter
    if(result.length === 0) {
        displayContent.forEach((item, index) => {
             result.push({ title: item.content.substring(0, 50) + '...', index });
        });
    }
    return result;
  }, [displayContent]);

  const loadAndFilterVoices = useCallback(() => {
    const allVoices = window.speechSynthesis.getVoices();
    if (allVoices.length === 0) {
      return; // Wait for onvoiceschanged to fire
    }

    const findVoice = (
      langCodes: string[],
      keywords: string[],
    ): SpeechSynthesisVoice | undefined => {
      return allVoices.find(voice =>
        langCodes.some(lc => voice.lang.toLowerCase().startsWith(lc)) &&
        keywords.some(kw => voice.name.toLowerCase().includes(kw))
      );
    };

    const voiceConfig = [
      // Mandarin
      { lang: ['zh'], keywords: ['female', '女', 'xiaoxiao', 'huihui'] },
      { lang: ['zh'], keywords: ['male', '男', 'kangkang', 'yaoyao'] },
      // English
      { lang: ['en'], keywords: ['female', 'woman', 'zira', 'samantha', 'susan'] },
      { lang: ['en'], keywords: ['male', 'man', 'david', 'mark', 'alex'] },
      // Bahasa (Indonesian/Malaysian)
      { lang: ['id', 'ms'], keywords: ['female', 'wanita', 'perempuan', 'damayanti'] },
      { lang: ['id', 'ms'], keywords: ['male', 'pria', 'lelaki'] },
    ];
    
    const filteredVoices = voiceConfig
        .map(config => findVoice(config.lang, config.keywords))
        .filter((v): v is SpeechSynthesisVoice => v !== undefined);

    const uniqueVoices = Array.from(new Set(filteredVoices));
    setVoices(uniqueVoices);

    if (uniqueVoices.length > 0) {
      if (!selectedVoice || !uniqueVoices.some(v => v.name === selectedVoice.name)) {
        const sourceLangVoice = uniqueVoices.find(v => v.lang.startsWith(sourceLanguage.split('-')[0]));
        setSelectedVoice(sourceLangVoice || uniqueVoices.find(v => v.lang.startsWith('en')) || uniqueVoices[0]);
      }
    } else {
      setSelectedVoice(null); // No voices found that match criteria
    }
  }, [selectedVoice, sourceLanguage]);

  useEffect(() => {
    const allVoices = window.speechSynthesis.getVoices();
    if (allVoices.length) {
      loadAndFilterVoices();
    }
    window.speechSynthesis.onvoiceschanged = loadAndFilterVoices;

    return () => {
      window.speechSynthesis.cancel();
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [loadAndFilterVoices]);
  
  const playText = useCallback((text: string) => {
    if (!selectedVoice) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = selectedVoice;
    utterance.rate = rate;
    utterance.pitch = pitch;

    utterance.onend = () => {
      if (currentChapterIndex < displayContent.length - 1) {
        const nextChapter = currentChapterIndex + 1;
        setCurrentChapterIndex(nextChapter);
      } else {
        setPlaybackState('stopped');
      }
    };
    
    window.speechSynthesis.speak(utterance);
  }, [selectedVoice, rate, pitch, currentChapterIndex, displayContent]);

  useEffect(() => {
    if (playbackState === 'playing' && !isTranslating) {
      const textToPlay = displayContent.slice(currentChapterIndex).map(c => c.content).join(' ');
      playText(textToPlay);
    } else {
      window.speechSynthesis.cancel();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playbackState, currentChapterIndex, selectedVoice, rate, pitch, displayContent, isTranslating]);


  const handlePlay = useCallback(() => setPlaybackState('playing'), []);
  const handlePause = useCallback(() => {
    window.speechSynthesis.pause();
    setPlaybackState('paused');
  }, []);
  const handleResume = useCallback(() => {
    window.speechSynthesis.resume();
    setPlaybackState('playing');
  }, []);
  const handleStop = useCallback(() => {
    setPlaybackState('stopped');
    setCurrentChapterIndex(0);
  }, []);

  const handleNext = useCallback(() => {
    const currentMainChapter = chapters.find(c => c.index <= currentChapterIndex);
    const currentMainChapterIndex = chapters.findIndex(c => c.index === currentMainChapter?.index);

    if (currentMainChapterIndex < chapters.length - 1) {
        const nextChapter = chapters[currentMainChapterIndex + 1];
        setCurrentChapterIndex(nextChapter.index);
        if(playbackState === 'paused') setPlaybackState('playing');
    }
  }, [currentChapterIndex, chapters, playbackState]);

  const handlePrev = useCallback(() => {
     const currentMainChapter = chapters.find(c => c.index <= currentChapterIndex);
     const currentMainChapterIndex = chapters.findIndex(c => c.index === currentMainChapter?.index);

    if (currentMainChapterIndex > 0) {
        const prevChapter = chapters[currentMainChapterIndex - 1];
        setCurrentChapterIndex(prevChapter.index);
        if(playbackState === 'paused') setPlaybackState('playing');
    }
  }, [currentChapterIndex, chapters, playbackState]);

  return (
    <div className="flex flex-col h-full">
        <div className="flex items-center justify-between mb-4">
            <button onClick={onReset} className="flex items-center text-highlight hover:text-teal-accent transition-colors">
                <ChevronLeftIcon className="w-5 h-5 mr-1" />
                Back to Upload
            </button>
            <h2 className="text-xl font-bold text-text-main truncate" title={fileName}>{fileName}</h2>
            <div className="w-36" /> {/* Placeholder to balance header */}
        </div>

      <div className="flex-grow flex flex-col overflow-hidden">
        <main className="bg-primary p-6 rounded-lg overflow-y-auto h-[55vh] md:h-auto relative flex-1">
          {isTranslating && (
            <div className="absolute inset-0 bg-primary/80 flex flex-col items-center justify-center z-10 rounded-lg">
                <LoadingSpinner />
                <p className="text-highlight mt-4">Translating to {selectedVoice?.lang}...</p>
            </div>
          )}
          {translationError && (
            <div className="absolute top-2 right-2 bg-red-500/30 text-red-300 p-2 rounded-md text-sm z-20">
                {translationError}
            </div>
          )}
          <AudioOnlyPlaceholder />
        </main>
      </div>

      <footer className="mt-4 pt-4 border-t border-accent">
        <PlayerControls
          playbackState={playbackState}
          onPlay={handlePlay}
          onPause={handlePause}
          onResume={handleResume}
          onStop={handleStop}
          onNext={handleNext}
          onPrev={handlePrev}
          rate={rate}
          onRateChange={setRate}
          pitch={pitch}
          onPitchChange={setPitch}
          voices={voices}
          selectedVoice={selectedVoice}
          onVoiceChange={setSelectedVoice}
        />
        <VoiceCommander
          onPlay={handlePlay}
          onPause={handlePause}
          onStop={handleStop}
          onNext={handleNext}
          onPrev={handlePrev}
        />
      </footer>
    </div>
  );
};