import { GoogleGenAI, Modality } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

function fileToGenerativePart(file: File) {
  return new Promise<{ mimeType: string; data: string }>((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      if (typeof reader.result !== 'string') {
        return reject(new Error("Failed to read file as base64 string"));
      }
      // result is "data:mime/type;base64,..."
      const [header, data] = reader.result.split(',');
      if (!header || !data) {
        return reject(new Error("Invalid base64 string format"));
      }
      const mimeType = header.split(':')[1].split(';')[0];
      resolve({ mimeType, data });
    };
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

export const extractFace = async (imageFile: File): Promise<string> => {
  const imagePart = {
    inlineData: await fileToGenerativePart(imageFile),
  };
  const textPart = {
    text: "Your task is to isolate the person's face from the image. Output a clean portrait of ONLY the face and neck. You MUST remove the original hair, clothes, and background. Place the face on a solid, neutral black background. The output must be ONLY the image, with no added text.",
  };

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-image-preview',
    contents: [imagePart, textPart],
    config: {
      responseModalities: [Modality.IMAGE, Modality.TEXT],
    },
  });

  const candidate = response.candidates?.[0];
  if (!candidate) {
    throw new Error("Face extraction failed: The model returned an empty response. This could be due to a network issue or if the image was blocked.");
  }

  const image = candidate.content?.parts?.find(part => part.inlineData)?.inlineData;
  
  if (image?.data) {
    return `data:${image.mimeType};base64,${image.data}`;
  }

  // If no image, check for a text explanation or safety reason.
  const textExplanation = candidate.content?.parts?.find(part => part.text)?.text;
  if (textExplanation) {
    console.error("Gemini API returned text during face extraction:", textExplanation);
    throw new Error(`Face extraction failed. The AI model responded: "${textExplanation}"`);
  }
  
  if (candidate.finishReason === 'SAFETY') {
    throw new Error("Face extraction failed because the uploaded image was flagged for safety reasons. Please try a different photo.");
  }

  throw new Error("Face extraction failed. The model did not return an image. Please try a different photo with a clearer view of the face.");
};

export const applyHairstyle = async (faceBase64: string, hairstylePrompt: string): Promise<string> => {
  const mimeType = faceBase64.substring(5, faceBase64.indexOf(';'));
  const data = faceBase64.split(',')[1];

  const facePart = {
    inlineData: { mimeType, data },
  };
  const textPart = {
    text: `Your task is to add a new hairstyle to the provided image of a person's face. 
It is critical that you **preserve the person's identity and facial features exactly as they are in the input image**. 
Do not change their face, skin tone, eye color, or expression.

The only changes you must make are:
1.  **Add a new hairstyle**: The new hairstyle should be '${hairstylePrompt}'. Fit this hairstyle realistically to the person's head shape, forehead, and hairline. It must look natural, not like a wig.
2.  **Add Clothing**: Dress the person in a simple, plain white crew-neck t-shirt.
3.  **Set Background**: Place the person against a neutral, light gray studio background.

**Output instructions**:
- The final image must be a high-quality, photorealistic portrait.
- The lighting on the new hair and clothing must match the lighting on the face from the original image.
- Do not add any text or watermarks. The output must only be the image.`,
  };

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-image-preview',
    contents: [facePart, textPart],
    config: {
      responseModalities: [Modality.IMAGE, Modality.TEXT],
    },
  });

  const image = response.candidates?.[0]?.content?.parts?.find(part => part.inlineData)?.inlineData;
  if (!image || !image.data) {
    throw new Error(`Hairstyle generation failed for: ${hairstylePrompt}. The model did not return an image.`);
  }

  return `data:${image.mimeType};base64,${image.data}`;
};