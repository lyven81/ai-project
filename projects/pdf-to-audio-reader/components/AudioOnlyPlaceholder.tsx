import React from 'react';
import { SoundWaveIcon } from './icons/SoundWaveIcon';

export const AudioOnlyPlaceholder: React.FC = () => {
    return (
        <div className="flex flex-col items-center justify-center h-full text-center text-accent">
            <SoundWaveIcon className="w-24 h-24 mb-6" />
            <h2 className="text-2xl font-bold text-highlight">Audio-Only Mode</h2>
            <p className="mt-2 text-text-dim">
                Use the controls below to play, pause, and navigate the audio.
            </p>
        </div>
    );
};
