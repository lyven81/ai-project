
import { AgeGroup, DrawingStyle } from './types';

export const AGE_GROUPS: AgeGroup[] = [
  { label: 'Toddler (3-5)', prompt: 'very simple with thick, bold outlines' },
  { label: 'Kid (6-9)', prompt: 'simple with clear outlines' },
  { label: 'Pre-teen (10-12)', prompt: 'detailed and intricate with fine lines' },
];

export const DRAWING_STYLES: DrawingStyle[] = [
  { label: 'Cartoonish', prompt: 'in a fun, friendly cartoon style' },
  { label: 'Doodle', prompt: 'in a whimsical, hand-drawn doodle style' },
  { label: 'Realistic', prompt: 'in a more realistic, detailed line art style' },
];
