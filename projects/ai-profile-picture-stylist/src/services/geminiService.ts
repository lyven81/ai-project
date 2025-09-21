
import { GoogleGenAI, Modality, GenerateContentResponse, Type } from "@google/genai";
import { getPrompts } from '../constants';
import { GeneratedImage } from '../types';

if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable is not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

export async function countPeopleInImage(imagePreviewUrl: string): Promise<number> {
    const mimeTypeMatch = imagePreviewUrl.match(/data:(image\/\w+);base64,/);
    if (!mimeTypeMatch) {
        throw new Error("Invalid image data URL.");
    }
    const mimeType = mimeTypeMatch[1];
    const base64Image = imagePreviewUrl.split(',')[1];

    const imagePart = {
        inlineData: {
            data: base64Image,
            mimeType: mimeType,
        },
    };

    const textPart = {
        text: 'Analyze the image and count the number of people visible. Respond with only a JSON object containing a single key "personCount" with a numerical value.',
    };

    try {
        const response: GenerateContentResponse = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: { parts: [imagePart, textPart] },
            config: {
                responseMimeType: 'application/json',
                responseSchema: {
                    type: Type.OBJECT,
                    properties: {
                        personCount: {
                            type: Type.NUMBER,
                            description: 'The number of people in the image.'
                        }
                    }
                }
            }
        });
        
        const jsonString = response.text;
        const result = JSON.parse(jsonString);
        
        if (typeof result.personCount === 'number') {
            return result.personCount;
        } else {
            throw new Error('Invalid response format from person counting API.');
        }

    } catch (error) {
        console.error('Error counting people in image:', error);
        throw new Error('Failed to analyze the image content.');
    }
}


async function generateSingleStyledImage(base64Image: string, mimeType: string, prompt: string): Promise<string> {
    const imagePart = {
        inlineData: {
            data: base64Image,
            mimeType: mimeType,
        },
    };

    const textPart = {
        text: prompt,
    };

    try {
        const response: GenerateContentResponse = await ai.models.generateContent({
            model: 'gemini-2.5-flash-image-preview',
            contents: {
                parts: [imagePart, textPart],
            },
            config: {
                responseModalities: [Modality.IMAGE, Modality.TEXT],
            },
        });
        
        // Find the image part in the response
        const imagePartResponse = response.candidates?.[0]?.content?.parts?.find(part => part.inlineData);

        if (imagePartResponse?.inlineData) {
            const base64ImageBytes: string = imagePartResponse.inlineData.data;
            return `data:${imagePartResponse.inlineData.mimeType};base64,${base64ImageBytes}`;
        } else {
            // Check for safety ratings or other reasons for blockage
            const safetyRatings = response.candidates?.[0]?.safetyRatings;
            if (safetyRatings && safetyRatings.some(r => r.probability !== 'NEGLIGIBLE')) {
                console.error("Image generation blocked due to safety ratings:", safetyRatings);
                throw new Error("The image could not be generated due to safety policies. Please try a different photo.");
            }
            console.error("No image data in response:", response);
            throw new Error('No image data found in the API response.');
        }
    } catch (error) {
        console.error('Error generating image with Gemini:', error);
        throw new Error('Failed to communicate with the image generation service.');
    }
}

export const generateStyledImages = async (imagePreviewUrl: string, personCount: number): Promise<GeneratedImage[]> => {
    const mimeTypeMatch = imagePreviewUrl.match(/data:(image\/\w+);base64,/);
    if (!mimeTypeMatch) {
        throw new Error("Invalid image data URL.");
    }
    const mimeType = mimeTypeMatch[1];
    const base64Image = imagePreviewUrl.split(',')[1];

    const STYLES = getPrompts(personCount);

    const imagePromises = STYLES.map(style => 
        generateSingleStyledImage(base64Image, mimeType, style.prompt)
            .then(src => ({ ...style, src }))
            .catch(error => {
                console.error(`Failed to generate style ${style.title}:`, error);
                // Return a placeholder or error state for this specific image
                return { ...style, src: '', error: `Failed to generate: ${error.message}` };
            })
    );

    const results = await Promise.all(imagePromises);
    
    // Filter out any that completely failed and only return successful ones
    return results.filter(result => result.src);
};
