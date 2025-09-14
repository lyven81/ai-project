import React, { useMemo } from 'react';
import { PlayIcon } from './icons/PlayIcon';
import { PauseIcon } from './icons/PauseIcon';
import { StopIcon } from './icons/StopIcon';
import { ForwardIcon } from './icons/ForwardIcon';
import { BackwardIcon } from './icons/BackwardIcon';

interface PlayerControlsProps {
  playbackState: 'playing' | 'paused' | 'stopped';
  onPlay: () => void;
  onPause: () => void;
  onResume: () => void;
  onStop: () => void;
  onNext: () => void;
  onPrev: () => void;
  rate: number;
  onRateChange: (rate: number) => void;
  pitch: number;
  onPitchChange: (pitch: number) => void;
  voices: SpeechSynthesisVoice[];
  selectedVoice: SpeechSynthesisVoice | null;
  onVoiceChange: (voice: SpeechSynthesisVoice | null) => void;
}

const ControlButton: React.FC<{ onClick: () => void; children: React.ReactNode; title: string; className?: string; disabled?: boolean }> = ({ onClick, children, title, className = '', disabled }) => (
    <button onClick={onClick} title={title} disabled={disabled} className={`p-2 rounded-full bg-accent hover:bg-highlight text-text-main transition-all focus:outline-none focus:ring-2 focus:ring-teal-accent disabled:opacity-50 disabled:cursor-not-allowed ${className}`}>
        {children}
    </button>
);


export const PlayerControls: React.FC<PlayerControlsProps> = ({
  playbackState,
  onPlay,
  onPause,
  onResume,
  onStop,
  onNext,
  onPrev,
  rate,
  onRateChange,
  pitch,
  onPitchChange,
  voices,
  selectedVoice,
  onVoiceChange,
}) => {
    
    const groupedVoices = useMemo(() => {
        return voices.reduce((acc, voice) => {
            let lang = voice.lang.split('-')[0];
            if (lang === 'id' || lang === 'ms') {
                lang = 'bahasa';
            }
            if (!acc[lang]) {
                acc[lang] = [];
            }
            acc[lang].push(voice);
            return acc;
        }, {} as Record<string, SpeechSynthesisVoice[]>);
    }, [voices]);


  return (
    <div className="space-y-4">
      <div className="flex items-center justify-center gap-4">
        <ControlButton onClick={onPrev} title="Previous Chapter"><BackwardIcon className="w-6 h-6" /></ControlButton>
        
        {playbackState === 'stopped' && <ControlButton onClick={onPlay} title="Play" className="w-16 h-16 bg-teal-accent text-primary"><PlayIcon className="w-10 h-10" /></ControlButton>}
        {playbackState === 'playing' && <ControlButton onClick={onPause} title="Pause" className="w-16 h-16 bg-teal-accent text-primary"><PauseIcon className="w-10 h-10" /></ControlButton>}
        {playbackState === 'paused' && <ControlButton onClick={onResume} title="Resume" className="w-16 h-16 bg-teal-accent text-primary"><PlayIcon className="w-10 h-10" /></ControlButton>}

        <ControlButton onClick={onStop} title="Stop" disabled={playbackState === 'stopped'}><StopIcon className="w-6 h-6" /></ControlButton>
        <ControlButton onClick={onNext} title="Next Chapter"><ForwardIcon className="w-6 h-6" /></ControlButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        <div className="flex items-center gap-2">
            <label htmlFor="voice-select" className="text-sm text-text-dim whitespace-nowrap">Voice:</label>
            <select
                id="voice-select"
                value={selectedVoice?.name || ''}
                onChange={(e) => onVoiceChange(voices.find(v => v.name === e.target.value) || null)}
                className="w-full bg-accent border-highlight rounded p-2 text-text-main focus:outline-none focus:ring-2 focus:ring-teal-accent"
                disabled={voices.length === 0}
            >
              {voices.length === 0 && <option>No specific voices found</option>}
                {Object.entries(groupedVoices).map(([lang, voiceList]) => (
                    <optgroup label={lang === 'bahasa' ? 'Bahasa' : lang.toUpperCase()} key={lang}>
                        {voiceList.map(voice => (
                            <option key={voice.name} value={voice.name}>{voice.name} ({voice.lang})</option>
                        ))}
                    </optgroup>
                ))}
            </select>
        </div>

        <div className="flex gap-4">
            <div className="flex-1 flex items-center gap-2">
                <label className="text-sm text-text-dim">Speed: {rate.toFixed(1)}x</label>
                <input type="range" min="0.5" max="2" step="0.1" value={rate} onChange={(e) => onRateChange(parseFloat(e.target.value))} className="w-full accent-teal-accent" />
            </div>
            <div className="flex-1 flex items-center gap-2">
                <label className="text-sm text-text-dim">Pitch: {pitch.toFixed(1)}</label>
                <input type="range" min="0" max="2" step="0.1" value={pitch} onChange={(e) => onPitchChange(parseFloat(e.target.value))} className="w-full accent-teal-accent" />
            </div>
        </div>
      </div>
      <div className="text-center">
          <button onClick={() => alert('Feature in development. Requires a server backend for audio processing.')} className="text-sm text-highlight hover:text-teal-accent transition-colors">Download Audio (MP3)</button>
      </div>
    </div>
  );
};