import React, { useState, useEffect, useCallback } from 'react';
import { PuzzlePiece as PuzzlePieceType } from '../types';
import { PuzzlePiece } from './PuzzlePiece';
import { PrintablePuzzle } from './PrintablePuzzle';

interface PuzzleBoardProps {
  imageSrc: string;
  gridSize: number;
  theme: string;
  onNewPuzzle: () => void;
}

export function PuzzleBoard({ imageSrc, gridSize, theme, onNewPuzzle }: PuzzleBoardProps) {
  const [pieces, setPieces] = useState<PuzzlePieceType[]>([]);
  const [isSolved, setIsSolved] = useState(false);
  const [draggedItem, setDraggedItem] = useState<PuzzlePieceType | null>(null);
  const [showHint, setShowHint] = useState(false);

  const shufflePieces = useCallback((arr: PuzzlePieceType[]) => {
    const shuffled = [...arr];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i].currentIndex, shuffled[j].currentIndex] = [shuffled[j].currentIndex, shuffled[i].currentIndex];
    }
    return shuffled;
  }, []);

  const initializePuzzle = useCallback(() => {
    const newPieces: PuzzlePieceType[] = [];
    for (let i = 0; i < gridSize * gridSize; i++) {
      const row = Math.floor(i / gridSize);
      const col = i % gridSize;
      newPieces.push({
        id: i,
        originalIndex: i,
        currentIndex: i,
        style: {
          backgroundPosition: `${(col * 100) / (gridSize - 1)}% ${(row * 100) / (gridSize - 1)}%`,
          backgroundSize: `${gridSize * 100}% ${gridSize * 100}%`,
        },
      });
    }
    setPieces(shufflePieces(newPieces));
    setIsSolved(false);
    setShowHint(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gridSize, shufflePieces]);


  useEffect(() => {
    initializePuzzle();
  }, [initializePuzzle]);
  
  useEffect(() => {
    const checkSolved = () => {
      if (pieces.length === 0) return false;
      return pieces.every(p => p.currentIndex === p.originalIndex);
    };
    if(checkSolved()) {
        setIsSolved(true);
        setShowHint(false);
    }
  }, [pieces]);


  const handleDragStart = (piece: PuzzlePieceType) => {
    setDraggedItem(piece);
  };

  const handleDrop = (targetPiece: PuzzlePieceType) => {
    if (!draggedItem) return;

    setPieces(currentPieces => {
        const newPieces = [...currentPieces];
        const draggedPieceIndexInArray = newPieces.findIndex(p => p.id === draggedItem.id);
        const targetPieceIndexInArray = newPieces.findIndex(p => p.id === targetPiece.id);

        if(draggedPieceIndexInArray !== -1 && targetPieceIndexInArray !== -1) {
            const tempIndex = newPieces[draggedPieceIndexInArray].currentIndex;
            newPieces[draggedPieceIndexInArray].currentIndex = newPieces[targetPieceIndexInArray].currentIndex;
            newPieces[targetPieceIndexInArray].currentIndex = tempIndex;
        }

        return newPieces;
    });
    setDraggedItem(null);
  };
  
  const sortedPieces = [...pieces].sort((a,b) => a.currentIndex - b.currentIndex);

  return (
    <div className="flex flex-col items-center gap-6 w-full max-w-4xl">
      <div className="relative w-full max-w-xl aspect-square">
        <div
          className="grid gap-1 bg-slate-700 p-1 rounded-md shadow-lg"
          style={{ gridTemplateColumns: `repeat(${gridSize}, 1fr)` }}
        >
          {sortedPieces.map((piece) => (
            <PuzzlePiece
              key={piece.id}
              piece={piece}
              imageSrc={imageSrc}
              isSolved={isSolved}
              onDragStart={handleDragStart}
              onDrop={handleDrop}
            />
          ))}
        </div>
        {showHint && !isSolved && (
          <div className="absolute inset-0 bg-black/70 flex items-center justify-center rounded-md backdrop-blur-sm p-2 transition-opacity duration-300">
            <img src={imageSrc} alt="Solved puzzle hint" className="max-w-full max-h-full object-contain rounded-md shadow-lg border-2 border-sky-400"/>
          </div>
        )}
        {isSolved && (
          <div className="absolute inset-0 bg-black/70 flex flex-col items-center justify-center rounded-md backdrop-blur-sm">
            <h2 className="text-4xl font-bold text-emerald-400 mb-2">Congratulations!</h2>
            <p className="text-xl text-slate-200">You solved the "{theme}" puzzle!</p>
          </div>
        )}
      </div>
      <div className="flex flex-wrap items-center justify-center gap-4">
        <button
            onClick={onNewPuzzle}
            className="px-6 py-2 bg-sky-600 text-white font-semibold rounded-md hover:bg-sky-500 transition-colors"
        >
            New Puzzle
        </button>
        <button
            onClick={() => initializePuzzle()}
            className="px-6 py-2 bg-slate-700 text-white font-semibold rounded-md hover:bg-slate-600 transition-colors"
        >
            Shuffle
        </button>
        <button
            onClick={() => setShowHint(prev => !prev)}
            disabled={isSolved}
            className="px-6 py-2 bg-purple-600 text-white font-semibold rounded-md hover:bg-purple-500 transition-colors disabled:bg-slate-800 disabled:text-slate-400 disabled:cursor-not-allowed"
        >
            {showHint ? 'Hide Hint' : 'Show Hint'}
        </button>
         <button
            onClick={() => window.print()}
            className="px-6 py-2 bg-slate-700 text-white font-semibold rounded-md hover:bg-slate-600 transition-colors print:hidden"
        >
            Print
        </button>
      </div>
      <PrintablePuzzle imageSrc={imageSrc} gridSize={gridSize} theme={theme} />
    </div>
  );
}