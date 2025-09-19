import { GoogleGenAI, Modality } from "@google/genai";

const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve((reader.result as string).split(',')[1]);
        reader.onerror = (error) => reject(error);
    });
};

const getMimeType = (file: File): string => {
    return file.type;
};


export const generatePolaroidImages = async (
    image1: File,
    image2: File,
    image3: File,
    posePrompts: string[]
): Promise<string[]> => {
    
    if (!process.env.API_KEY) {
        // This check prevents the app from crashing if the key is missing,
        // but the UI layer should ideally prevent this function from being called.
        throw new Error("API_KEY is not configured in the environment.");
    }
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    
    const base64Image1 = await fileToBase64(image1);
    const base64Image2 = await fileToBase64(image2);
    const base64Image3 = await fileToBase64(image3);
    const mimeType1 = getMimeType(image1);
    const mimeType2 = getMimeType(image2);
    const mimeType3 = getMimeType(image3);

    const imagePart1 = { inlineData: { data: base64Image1, mimeType: mimeType1 } };
    const imagePart2 = { inlineData: { data: base64Image2, mimeType: mimeType2 } };
    const imagePart3 = { inlineData: { data: base64Image3, mimeType: mimeType3 } };

    const generationPromises = posePrompts.map(async (posePrompt) => {
        const fullPrompt = `Using the three provided images of people, generate a new image of them together. The output image must have a 1:1 square aspect ratio. The style should be that of a candid Polaroid photo, with a slight blur and a consistent flash-like light source as if taken in a dark room. Replace the background with white curtains. IMPORTANT: Do not alter the faces of the people from the original photos. The final image should feel like an ordinary, candid moment with no prominent props. ${posePrompt}`;
        
        const textPart = { text: fullPrompt };

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-image-preview',
            contents: {
                parts: [imagePart1, imagePart2, imagePart3, textPart],
            },
            config: {
                responseModalities: [Modality.IMAGE, Modality.TEXT],
            },
        });

        // Find the image part in the response
        const imagePart = response.candidates?.[0]?.content?.parts?.find(part => part.inlineData);
        if (imagePart && imagePart.inlineData) {
            return `data:${imagePart.inlineData.mimeType};base64,${imagePart.inlineData.data}`;
        }
        
        // Fallback or error if no image is returned
        const textResponse = response.text;
        throw new Error(`Image generation failed for one of the poses. Model response: ${textResponse || 'No text response'}`);
    });

    return Promise.all(generationPromises);
};