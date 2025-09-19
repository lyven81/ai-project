
export enum Difficulty {
  EASY = 3,   // 3x3 for toddlers
  MEDIUM = 4, // 4x4 for children
  HARD = 5,   // 5x5 for adults
}

export interface PuzzlePiece {
  id: number;
  originalIndex: number;
  currentIndex: number;
  style: {
    backgroundPosition: string;
    backgroundSize: string;
  };
}
