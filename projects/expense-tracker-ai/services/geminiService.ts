
import { GoogleGenAI, Type } from "@google/genai";
import { expenseCategories, ExpenseData } from "../types";

// This is a placeholder. In a real app, use environment variables.
const API_KEY = process.env.API_KEY;
if (!API_KEY) {
  console.warn("API_KEY environment variable not set. Using placeholder. AI features will not work.");
}
const ai = new GoogleGenAI({ apiKey: API_KEY || "YOUR_API_KEY_HERE" });

const expenseSchema = {
  type: Type.OBJECT,
  properties: {
    merchant: {
      type: Type.STRING,
      description: "The name of the merchant or store.",
    },
    date: {
      type: Type.STRING,
      description: "The date of the purchase in YYYY-MM-DD format. Infer from the receipt.",
    },
    total: {
      type: Type.NUMBER,
      description: "The final total amount of the bill after any taxes or discounts.",
    },
    currency: {
      type: Type.STRING,
      description: "The 3-letter currency code (e.g., USD, EUR, JPY). Default to USD if not found.",
    },
    category: {
      type: Type.STRING,
      description: `Classify the expense into one of the following categories.`,
      enum: [...expenseCategories],
    },
    items: {
      type: Type.ARRAY,
      description: "A list of individual items purchased with their prices. If not available, return an empty array.",
      items: {
        type: Type.OBJECT,
        properties: {
          name: { type: Type.STRING, description: "Name of the item." },
          price: { type: Type.NUMBER, description: "Price of the item." },
        },
         required: ['name', 'price'],
      },
    },
  },
  required: ["merchant", "date", "total", "category", "currency"],
};

export const extractExpenseDataFromImage = async (
  base64Image: string,
  mimeType: string
): Promise<ExpenseData> => {
  if (!API_KEY) {
    throw new Error("Gemini API key is not configured.");
  }

  const imagePart = {
    inlineData: {
      data: base64Image,
      mimeType: mimeType,
    },
  };

  const textPart = {
    text: "Analyze this receipt image and extract the expense details. Provide the output in a structured JSON format. If a detail is unclear, make a reasonable guess.",
  };

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: { parts: [imagePart, textPart] },
    config: {
      responseMimeType: "application/json",
      responseSchema: expenseSchema,
    },
  });
  
  const jsonText = response.text.trim();
  try {
    const parsedData = JSON.parse(jsonText);
    
    // Validate category
    if (!expenseCategories.includes(parsedData.category)) {
        parsedData.category = "Other";
    }

    return parsedData as ExpenseData;
  } catch (error) {
    console.error("Failed to parse JSON response from Gemini:", jsonText, error);
    throw new Error("Could not extract expense data. The AI returned an invalid format.");
  }
};
