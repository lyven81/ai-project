
import { GoogleGenAI, Type } from "@google/genai";
import { ParsedContent } from '../types';

if (!process.env.API_KEY) {
  throw new Error("API_KEY environment variable is not set.");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const structureWithLangSchema = {
    type: Type.OBJECT,
    properties: {
        language: {
            type: Type.STRING,
            description: "The BCP-47 language code of the document's main language (e.g., 'en-US', 'zh-CN', 'es-ES')."
        },
        content: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                type: {
                  type: Type.STRING,
                  description: "Type of content: heading_1, heading_2, paragraph, image_description, or list_item.",
                  enum: ['heading_1', 'heading_2', 'paragraph', 'image_description', 'list_item']
                },
                content: {
                  type: Type.STRING,
                  description: "The text content for this section."
                },
              },
              required: ["type", "content"],
            }
        }
    },
    required: ["language", "content"],
};

export const structurePdfText = async (text: string): Promise<{ structuredContent: ParsedContent[], language: string }> => {
  try {
    const prompt = `Analyze the following document text. First, identify its primary language and provide its BCP-47 code (e.g., 'en-US', 'zh-CN', 'es-ES'). Second, structure it into a clear JSON format. Identify headings, paragraphs, and any text that appears to describe images, charts, or tables. Use 'heading_1' for main titles/chapters, 'heading_2' for subheadings, and 'paragraph' for body text. Use 'image_description' for text describing visuals and 'list_item' for items in a list. Ensure the output is a valid JSON object according to the provided schema. Here is the text:\n\n---\n\n${text.substring(0, 30000)}`; // Truncate to avoid exceeding token limits

    const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            responseSchema: structureWithLangSchema,
        },
    });
    
    const jsonString = response.text;
    const parsedJson = JSON.parse(jsonString);

    if (!parsedJson || !Array.isArray(parsedJson.content) || typeof parsedJson.language !== 'string') {
        throw new Error("AI response is not in the expected format ({language: string, content: array}).");
    }
    
    const structuredContent = parsedJson.content.filter((item: any) => item && typeof item.type === 'string' && typeof item.content === 'string');
    const language = parsedJson.language;

    return { structuredContent, language };

  } catch (error) {
    console.error("Error structuring PDF text with Gemini:", error);
    throw new Error("Failed to structure document content using AI. The document might be too complex or in an unsupported format.");
  }
};


const translationSchema = {
    type: Type.ARRAY,
    items: {
      type: Type.OBJECT,
      properties: {
        type: { type: Type.STRING },
        content: { type: Type.STRING }
      },
      required: ["type", "content"],
    }
};

export const translateContent = async (content: ParsedContent[], targetLanguage: string): Promise<ParsedContent[]> => {
    try {
        const contentToTranslate = JSON.stringify(content.map(item => ({type: item.type, content: item.content})));
        const prompt = `Translate the 'content' string in each object of the following JSON array to the language with BCP-47 code '${targetLanguage}'. Maintain the original 'type' for each object and the overall JSON array structure. Respond with only the translated JSON array.\n\n${contentToTranslate}`;

        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: translationSchema,
            },
        });

        const jsonString = response.text;
        const parsedJson = JSON.parse(jsonString);

        if (!Array.isArray(parsedJson)) {
            throw new Error("AI translation response is not in the expected array format.");
        }
        
        return parsedJson.filter(item => item && typeof item.type === 'string' && typeof item.content === 'string');

    } catch (error) {
        console.error(`Error translating content to ${targetLanguage}:`, error);
        throw new Error(`Failed to translate document to ${targetLanguage}.`);
    }
};
