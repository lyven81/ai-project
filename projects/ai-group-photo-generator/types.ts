export interface UploadedFile {
  id: string;
  file: File;
  preview: string;
}

// FIX: Add Theme type for ThemeSelector component.
export type Theme = 'Casual' | 'Formal' | 'Business' | 'Party' | 'Vintage' | 'Futuristic';
