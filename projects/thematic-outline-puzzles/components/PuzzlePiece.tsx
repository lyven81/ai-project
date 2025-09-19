
import React from 'react';
import { PuzzlePiece as PuzzlePieceType } from '../types';

interface PuzzlePieceProps {
  piece: PuzzlePieceType;
  imageSrc: string;
  isSolved: boolean;
  onDragStart: (piece: PuzzlePieceType) => void;
  onDrop: (piece: PuzzlePieceType) => void;
}

export function PuzzlePiece({ piece, imageSrc, isSolved, onDragStart, onDrop }: PuzzlePieceProps) {
  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div
      draggable={!isSolved}
      onDragStart={() => onDragStart(piece)}
      onDragOver={handleDragOver}
      onDrop={() => onDrop(piece)}
      className={`aspect-square transition-all duration-300 ${isSolved ? 'border-none' : 'cursor-grab active:cursor-grabbing opacity-90 hover:opacity-100 hover:scale-105'}`}
      style={{
        backgroundImage: `url(${imageSrc})`,
        ...piece.style,
      }}
    />
  );
}
