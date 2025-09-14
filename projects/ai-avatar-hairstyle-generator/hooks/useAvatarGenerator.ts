
import { useState, useCallback } from 'react';
import { extractFace, applyHairstyle } from '../services/geminiService';

const HAIRSTYLE_PROMPTS = [
  "long, wavy brunette hair",
  "short, stylish pixie cut in blonde",
  "vibrant red, shoulder-length curly hair",
  "a sleek, black bob with bangs",
  "a modern silver-gray undercut",
  "a high ponytail with elegant braids",
  "natural-looking voluminous afro hairstyle",
  "messy, layered shag cut with highlights",
  "straight, platinum blonde long hair",
];

const useAvatarGenerator = () => {
  const [generatedAvatars, setGeneratedAvatars] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState<string | null>(null);

  const generateAvatars = useCallback(async (imageFile: File) => {
    setIsLoading(true);
    setError(null);
    setGeneratedAvatars([]);

    try {
      setLoadingMessage('Detecting and extracting face...');
      const faceBase64 = await extractFace(imageFile);

      setLoadingMessage('Generating 9 unique hairstyles...');
      const avatarPromises = HAIRSTYLE_PROMPTS.map(prompt => 
        applyHairstyle(faceBase64, prompt)
      );

      const avatars = await Promise.all(avatarPromises);
      setGeneratedAvatars(avatars);

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
