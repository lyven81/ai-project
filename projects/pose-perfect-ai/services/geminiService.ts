
import { GoogleGenAI, Modality } from "@google/genai";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
    throw new Error("API_KEY environment variable is not set.");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

export const generateImageFromPose = async (
    subjectBase64: string,
    subjectMimeType: string,
    poseBase64: string,
    poseMimeType: string,
    aspectRatio: string
): Promise<string | null> => {
    try {
        const model = 'gemini-2.5-flash-image-preview';

        // A more direct, structured prompt to guide the model precisely.
        // It clarifies the role of each image and the desired output.
        const prompt = `Follow these instructions precisely:
1. The **subject** is the person in the first image. You must preserve their face, features, clothing, and overall identity.
2. The **pose** is the body position shown in the second image.
3. Generate a new, photorealistic image of the **subject** adopting the exact **pose**.
4. The background must be a simple, clean, minimalist studio setting with soft, even lighting. Do not include any text or artifacts in the final image.
5. The final image must have an aspect ratio of ${aspectRatio}.`;

        const response = await ai.models.generateContent({
            model: model,
            contents: {
                // Reordering parts to have the text prompt first provides clearer context to the model before it processes the images.
                parts: [
                    { text: prompt },
                    { inlineData: { data: subjectBase64, mimeType: subjectMimeType } },
                    { inlineData: { data: poseBase64, mimeType: poseMimeType } },
                ],
            },
            config: {
                responseModalities: [Modality.IMAGE, Modality.TEXT],
            },
        });

        if (response.candidates && response.candidates.length > 0) {
            for (const part of response.candidates[0].content.parts) {
                if (part.inlineData) {
                    return part.inlineData.data;
                }
            }
        }
        
        // Improved error detection and reporting
        console.warn("No image part found in the Gemini response.", JSON.stringify(response, null, 2));

        if (response.candidates?.[0]?.finishReason === 'SAFETY') {
            throw new Error("Image generation was blocked due to safety policies. Please try using different images.");
        }
        
        if (response.promptFeedback?.blockReason) {
             throw new Error(`Request was blocked: ${response.promptFeedback.blockReason}. Please adjust your images.`);
        }

        return null;

    } catch (error) {
        console.error("Error calling Gemini API:", error);
        if (error instanceof Error) {
            // Re-throw specific errors to be displayed in the UI
            throw error;
        }
        throw new Error("Failed to generate image due to an API error. Please try again later.");
    }
};
