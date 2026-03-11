import { GoogleGenAI, Type, ThinkingLevel } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export interface HoroscopeData {
  date: string;
  reading: string;
  skyExplainer: string;
  snapshot: {
    planet: string;
    position: string;
    influence: string;
  }[];
}

export async function generateDailyHoroscope(sign: string, language: 'en' | 'zh' = 'en'): Promise<HoroscopeData> {
  const today = new Date().toISOString().split('T')[0];
  const langPrompt = language === 'zh' ? "in Mandarin Chinese (Simplified)" : "in English";
  
  const response = await ai.models.generateContent({
    model: "gemini-3-flash-preview",
    contents: `Generate a daily horoscope for ${sign} for the date ${today} ${langPrompt}. 
    Include:
    1. A personalized daily reading (about 100 words).
    2. A "Sky Explainer" that identifies 2-3 real planetary movements happening today and explains in plain English (or Mandarin if requested) why they affect ${sign}.
    3. A "Sky Snapshot" which is a list of 3 key planets, their current astrological position (e.g., "Mars in Leo"), and their brief influence.
    
    The tone should be grounded, credible, and atmospheric. All text output must be in ${language === 'zh' ? 'Mandarin Chinese' : 'English'}.`,
    config: {
      thinkingConfig: { thinkingLevel: ThinkingLevel.LOW },
      responseMimeType: "application/json",
      responseSchema: {
        type: Type.OBJECT,
        properties: {
          date: { type: Type.STRING },
          reading: { type: Type.STRING },
          skyExplainer: { type: Type.STRING },
          snapshot: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                planet: { type: Type.STRING },
                position: { type: Type.STRING },
                influence: { type: Type.STRING }
              },
              required: ["planet", "position", "influence"]
            }
          }
        },
        required: ["date", "reading", "skyExplainer", "snapshot"]
      }
    }
  });

  try {
    return JSON.parse(response.text);
  } catch (e) {
    console.error("Failed to parse Gemini response", e);
    throw new Error("Failed to generate horoscope");
  }
}
