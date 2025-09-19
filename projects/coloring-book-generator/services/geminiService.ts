
import { GoogleGenAI, Type } from "@google/genai";

const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  throw new Error("API_KEY environment variable not set");
}
const ai = new GoogleGenAI({ apiKey: API_KEY });

export async function generatePageIdeas(theme: string): Promise<string[]> {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: `Generate a list of 10 distinct, child-friendly subjects for coloring pages with the theme "${theme}". The subjects should be single, simple concepts. For example, for "sea animals", you could return ["A friendly dolphin", "A curious sea turtle", "A starfish on the sand"].`,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            ideas: {
              type: Type.ARRAY,
              items: {
                type: Type.STRING,
                description: 'A single coloring page subject or idea.',
              },
            },
          },
          required: ['ideas'],
        },
      },
    });

    const jsonText = response.text.trim();
    const result = JSON.parse(jsonText);

    if (result.ideas && Array.isArray(result.ideas) && result.ideas.length >= 10) {
      return result.ideas.slice(0, 10);
    } else {
      throw new Error("Invalid or insufficient ideas generated.");
    }
  } catch (error) {
    console.error("Error generating page ideas:", error);
    throw new Error("Failed to get ideas from AI. Please check the theme and try again.");
  }
}

export async function generateImage(subject: string, agePrompt: string, stylePrompt: string): Promise<string> {
  const prompt = `A black and white coloring book page for a child. The style is ${stylePrompt} and ${agePrompt}. The drawing is of: "${subject}". It must have clean lines, no shading or color, on a pure white background. The image should be centered and fill the space well.`;

  try {
    const response = await ai.models.generateImages({
      model: 'imagen-4.0-generate-001',
      prompt: prompt,
      config: {
        numberOfImages: 1,
        outputMimeType: 'image/png',
        aspectRatio: '1:1',
      },
    });

    if (response.generatedImages && response.generatedImages.length > 0) {
      return response.generatedImages[0].image.imageBytes;
    } else {
      throw new Error("No image was generated.");
    }
  } catch (error) {
    console.error(`Error generating image for subject "${subject}":`, error);
    // Fallback or retry logic could be implemented here
    throw new Error(`Failed to generate an image for "${subject}".`);
  }
}
