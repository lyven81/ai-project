
import { GoogleGenAI, Modality, Part } from "@google/genai";

const POSES = [
  'front-facing, full body shot',
  'side view, full body shot',
  'from the back, full body shot',
  'in a natural walking motion, full body shot'
];

const dataUrlToPart = (dataUrl: string): Part => {
  const [header, data] = dataUrl.split(',');
  const mimeType = header.match(/:(.*?);/)?.[1] || 'application/octet-stream';
  return {
    inlineData: {
      mimeType,
      data,
    },
  };
};

export const generateTryOnImages = async (
  personImage: string,
  garmentImages: string[]
): Promise<string[]> => {
  if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable not set");
  }
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  const tryOnPromises = POSES.map(async (pose) => {
    const personPart = dataUrlToPart(personImage);
    const garmentParts = garmentImages.map(dataUrlToPart);

    const textPrompt = `From the provided images, use the person in the first image as the model and the clothing items from the subsequent images. Generate a new, single, photorealistic image of the person wearing all the specified clothing items. The final image must show the person in a ${pose}. The setting should be a neutral, clean studio background to focus on the clothing. Ensure the clothing drapes and fits realistically on the person's body shape. Crucially, maintain the person's original facial features, hair, and overall identity from the source photo. Do not include any text or logos in the generated image.`;

    const allParts: Part[] = [personPart, ...garmentParts, { text: textPrompt }];
    
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash-image-preview',
        contents: { parts: allParts },
        config: {
          responseModalities: [Modality.IMAGE, Modality.TEXT],
        },
      });

      const imagePart = response.candidates?.[0]?.content?.parts.find(p => p.inlineData);
      
      if (imagePart && imagePart.inlineData) {
        const { mimeType, data } = imagePart.inlineData;
        return `data:${mimeType};base64,${data}`;
      }
      
      throw new Error(`No image was generated for the pose: ${pose}`);
    } catch (error) {
       console.error(`Error generating image for pose "${pose}":`, error);
       // Re-throw the error to be handled by the calling function in App.tsx
       throw new Error(`Failed to generate image for pose: ${pose}. Details in console.`);
    }
  });

  return Promise.all(tryOnPromises);
};
