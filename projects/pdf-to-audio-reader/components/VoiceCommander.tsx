
import React, { useState, useEffect, useRef } from 'react';
import { MicIcon } from './icons/MicIcon';

interface VoiceCommanderProps {
  onPlay: () => void;
  onPause: () => void;
  onStop: () => void;
  onNext: () => void;
  onPrev: () => void;
}

// Check for SpeechRecognition API
const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
const isSpeechRecognitionSupported = !!SpeechRecognition;

export const VoiceCommander: React.FC<VoiceCommanderProps> = ({ onPlay, onPause, onStop, onNext, onPrev }) => {
  const [isListening, setIsListening] = useState(false);
  const [feedback, setFeedback] = useState('');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (!isSpeechRecognitionSupported) {
      console.warn('Speech Recognition is not supported in this browser.');
      return;
    }
    
    recognitionRef.current = new SpeechRecognition();
    const recognition = recognitionRef.current;
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const command = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
      setFeedback(`Command heard: "${command}"`);
      
      if (command.includes('play') || command.includes('start')) {
        onPlay();
      } else if (command.includes('pause')) {
        onPause();
      } else if (command.includes('stop')) {
        onStop();
      } else if (command.includes('next')) {
        onNext();
      } else if (command.includes('previous') || command.includes('back')) {
        onPrev();
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error', event.error);
      setFeedback(`Error: ${event.error}`);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    return () => {
      recognition.stop();
    };
  }, [onPlay, onPause, onStop, onNext, onPrev]);

  const toggleListening = () => {
    if (!isSpeechRecognitionSupported) {
        alert("Sorry, your browser doesn't support voice commands.");
        return;
    }

    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      setFeedback('Listening...');
      recognitionRef.current?.start();
    }
    setIsListening(!isListening);
  };
  
  if (!isSpeechRecognitionSupported) return null;

  return (
    <div className="mt-4 flex flex-col items-center justify-center gap-2">
      <button onClick={toggleListening} className={`p-3 rounded-full transition-colors ${isListening ? 'bg-red-600 animate-pulse' : 'bg-accent hover:bg-highlight'}`}>
        <MicIcon className="w-6 h-6 text-text-main" />
      </button>
      <p className="text-sm text-text-dim h-4">{feedback}</p>
    </div>
  );
};
