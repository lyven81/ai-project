
import { useState, useCallback } from 'react';
import { generateExpression } from '../services/geminiService';

export interface AvatarData {
  src: string;
  prompt: string;
}

const EXPRESSION_PROMPTS = [
  "extreme happiness",
  "shocked",
  "furious anger",
  "crying dramatically",
  "evil smirk",
  "confused",
  "completely calm",
  "terrified",
  "blank face",
];

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
};

const useAvatarGenerator = () => {
  const [generatedAvatars, setGeneratedAvatars] = useState<AvatarData[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const generateAvatars = useCallback(async (imageFile: File) => {
    setIsLoading(true);
    setError(null);
    setGeneratedAvatars([]);

    try {
      setLoadingMessage('Preparing your photo...');
      const imageBase64 = await fileToBase64(imageFile);

      setLoadingMessage('Generating 9 unique expressions...');
      const avatarPromises = EXPRESSION_PROMPTS.map(prompt => 
        generateExpression(imageBase64, prompt)
      );

      const avatars = await Promise.all(avatarPromises);
      
      const avatarData = avatars.map((src, index) => ({
        src,
        prompt: EXPRESSION_PROMPTS[index],
      }));

      setGeneratedAvatars(avatarData);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
      console.error(errorMessage);
      setError(errorMessage);
    } finally {
      setIsLoading(false);
      setLoadingMessage('');
    }
  }, []);

  const reset = useCallback(() => {
    setGeneratedAvatars([]);
    setIsLoading(false);
    setLoadingMessage('');
    setError(null);
  }, []);

  return {
    generatedAvatars,
    isLoading,
    loadingMessage,
    error,
    generateAvatars,
    reset,
  };
};

export default useAvatarGenerator;