import { GoogleGenAI, Modality } from "@google/genai";

if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable is not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const fileToGenerativePart = (file: File): Promise<{mimeType: string, data: string}> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
        const base64Data = (reader.result as string).split(',')[1];
        resolve({
            mimeType: file.type,
            data: base64Data,
        });
    };
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
};

export const generateGroupImage = async (
    files: File[], 
    poseFile: File | null, 
    scene: string, 
    aspectRatio: string
): Promise<string> => {
    try {
        const allParts: ({inlineData: {mimeType: string, data: string}} | {text: string})[] = [];

        // Order of images is important for the prompt.
        // 1. Pose (optional)
        // 2. All people images
        if (poseFile) {
            allParts.push({ inlineData: await fileToGenerativePart(poseFile) });
        }
        
        const personImageParts = await Promise.all(
            files.map(file => fileToGenerativePart(file).then(part => ({ inlineData: part })))
        );
        allParts.push(...personImageParts);


        // Construct prompt
        let prompt = `Your task is to create a single, realistic, high-quality group photograph with a ${aspectRatio} aspect ratio. `;
        prompt += `You must include every person from all of the provided photos of people. `;

        if (poseFile) {
            prompt += `Arrange the people according to the pose reference provided in the first image. `;
        } else {
            prompt += `Arrange the people in a natural group pose. `;
        }

        prompt += `The scene should be: "${scene || 'a plain photo studio background.'}". `;
        prompt += `The people in the final image must be wearing the same clothing as in their original photos. `;
        prompt += `Ensure the final image is cohesive and looks like a real photograph. Ensure lighting, shadows, and perspective are consistent across all individuals and the environment. Adjust facial expressions for a friendly, positive mood. The result must be photorealistic. Do not add any text or captions to the image.`;
        
        allParts.push({ text: prompt });

        const contents = {
            parts: allParts,
        };

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash-image-preview',
            contents,
            config: {
                responseModalities: [Modality.IMAGE, Modality.TEXT],
            },
        });

        const imagePart = response.candidates?.[0]?.content?.parts?.find(part => part.inlineData);
        
        if (imagePart && imagePart.inlineData) {
            return `data:${imagePart.inlineData.mimeType};base64,${imagePart.inlineData.data}`;
        } else {
            const textPart = response.candidates?.[0]?.content?.parts?.find(part => part.text);
            if(textPart?.text) {
                throw new Error(`The model returned text instead of an image: ${textPart.text}`);
            }
            throw new Error("The AI model did not return a valid image. Please try adjusting your prompt or using different photos.");
        }

    } catch (error) {
        console.error("Error generating image with Gemini API:", error);
        throw new Error("Failed to generate image. The AI model may be experiencing issues or the request was blocked.");
    }
};