import { GoogleGenAI, Modality } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

export const generateExpression = async (imageBase64: string, expressionPrompt: string): Promise<string> => {
  const mimeType = imageBase64.substring(5, imageBase64.indexOf(';'));
  const data = imageBase64.split(',')[1];

  const imagePart = {
    inlineData: { mimeType, data },
  };
  
  const textPart = {
    text: `Your task is to alter the facial expression of the person in the provided image to show **'${expressionPrompt}'**.

**Critical rules for consistency**:
1.  **Identity Preservation**: You **must** preserve the person's identity, hair, face shape, skin tone, and all other physical features exactly as they are in the input image.
2.  **Clothing**: The person **must** be wearing a **simple, plain white crew-neck t-shirt**. This should be consistent in every generated image.
3.  **Composition**: The output image **must** be a **head-and-shoulders portrait**. The framing and zoom level must be consistent across all generated expressions.
4.  **Background & Lighting**: Place the person against a **clean, seamless white studio background** with **cinematic, soft lighting**.

**Output instructions**:
- The final image must be a high-quality, photorealistic portrait.
- The lighting on the face must be consistent and look natural.
- Do not add any text or watermarks. The output must only be the image.`,
  };

  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash-image-preview',
    contents: { 
        parts: [imagePart, textPart]
    },
    config: {
      responseModalities: [Modality.IMAGE, Modality.TEXT],
    },
  });

  const image = response.candidates?.[0]?.content?.parts?.find(part => part.inlineData)?.inlineData;
  if (!image || !image.data) {
    throw new Error(`Expression generation failed for: ${expressionPrompt}. The model did not return an image.`);
  }

  return `data:${image.mimeType};base64,${image.data}`;
};