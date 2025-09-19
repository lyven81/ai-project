
import React from 'react';

interface PrintablePuzzleProps {
    imageSrc: string;
    gridSize: number;
    theme: string;
}

export function PrintablePuzzle({ imageSrc, gridSize, theme }: PrintablePuzzleProps) {
    const lines = Array.from({ length: gridSize - 1 });
    
    return (
        <div className="hidden print:block w-full text-black p-8">
            <h1 className="text-3xl font-bold mb-4 text-center">"{theme}" Puzzle</h1>
            <p className="text-center mb-8">Cut along the lines to create your puzzle!</p>
            <div className="relative w-[18cm] h-[18cm] mx-auto border-2 border-black">
                <img src={imageSrc} alt={`Puzzle theme: ${theme}`} className="w-full h-full object-cover" />
                
                {/* Vertical Lines */}
                {lines.map((_, i) => (
                    <div 
                        key={`v-${i}`}
                        className="absolute top-0 bottom-0 w-px bg-black opacity-50"
                        style={{ left: `${((i + 1) / gridSize) * 100}%` }}
                    ></div>
                ))}
                
                {/* Horizontal Lines */}
                {lines.map((_, i) => (
                    <div 
                        key={`h-${i}`}
                        className="absolute left-0 right-0 h-px bg-black opacity-50"
                        style={{ top: `${((i + 1) / gridSize) * 100}%` }}
                    ></div>
                ))}
            </div>
        </div>
    );
}
