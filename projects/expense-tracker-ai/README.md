# 💳 Expense Tracker AI

[![React](https://img.shields.io/badge/React-19.1+-blue?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue?logo=typescript)](https://typescriptlang.org/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI-orange?logo=google)](https://ai.google.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.2+-purple?logo=vite)](https://vitejs.dev/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=vercel)](https://ai.studio/apps/drive/1i4NXHqvfcItqJQcpYSTGZCotPCzAIFqc)

Intelligent expense tracking with AI-powered receipt processing using Google Gemini. Simply photograph your receipts and let AI extract all the expense details automatically - from merchant names to itemized purchases.

<div align="center">
<img width="1200" height="475" alt="Expense Tracker AI Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

## 🚀 Live Demo

**[🌟 View Live Demo](https://ai.studio/apps/drive/1i4NXHqvfcItqJQcpYSTGZCotPCzAIFqc)** | [📹 Video Demo](#)

## ✨ Features

- **🤖 AI Receipt Processing:** Advanced receipt analysis using Google Gemini AI
- **📸 Photo Upload:** Simply snap a photo of your receipt for instant processing
- **💰 Automatic Extraction:** Merchant, date, total, items, and prices extracted automatically
- **📊 Smart Analytics:** Visual expense tracking with interactive charts
- **📈 Time-Based Views:** Daily, Weekly, Monthly, and Yearly expense analysis
- **🏷️ Category Management:** Auto-categorization with 8 expense categories
- **💾 Local Storage:** All data persists locally in your browser
- **📱 Responsive Design:** Works seamlessly on desktop and mobile devices
- **🌙 Modern UI:** Clean interface with hover animations and transitions

## 🛠️ Tech Stack

**Frontend Framework:**
- **React 19.1+** - Latest React with modern features
- **TypeScript 5.8+** - Type-safe development
- **Vite 6.2+** - Fast build tool and dev server

**AI & Processing:**
- **Google Gemini AI** - Advanced OCR and data extraction from receipts
- **Custom Image Processing** - Base64 encoding and file handling
- **Smart Categorization** - AI-powered expense category suggestions

**Data Visualization:**
- **Recharts 3.2+** - Interactive charts and graphs
- **Date-fns 4.1+** - Date manipulation and formatting
- **Custom Analytics** - Time-based expense tracking

**Styling & UX:**
- **Tailwind CSS** - Utility-first CSS framework
- **Custom Components** - Reusable UI components
- **Responsive Design** - Mobile-first approach

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+**
- **Gemini API Key** from Google AI Studio

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lyven81/ai-project.git
   cd ai-project/projects/expense-tracker-ai
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env.local file
   echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env.local
   ```

4. **Start the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   Navigate to `http://localhost:5173`

## 📖 How It Works

### 1. Receipt Upload
- Click "Add Expense" to open the upload modal
- Take a photo or select an existing image of your receipt
- The AI automatically processes the image in real-time

### 2. AI Processing
- Gemini AI extracts merchant name, date, and total amount
- Individual items and their prices are identified and listed
- Expense category is automatically suggested based on merchant type

### 3. Review & Save
- Review the extracted data and make any necessary adjustments
- Add or remove individual items as needed
- Confirm and save the expense to your local storage

### 4. Analytics Dashboard
- View your expenses in interactive charts
- Switch between daily, weekly, monthly, and yearly views
- Track spending patterns by category
- Monitor recent transactions in the expense list

## 🎯 Expense Categories

- **🍕 Food** - Restaurants, groceries, cafes
- **🚗 Transport** - Gas, public transit, rideshare
- **⚡ Utilities** - Electricity, water, internet
- **🎬 Entertainment** - Movies, games, subscriptions
- **🛍️ Shopping** - Clothing, electronics, general retail
- **🏥 Health** - Medical, pharmacy, fitness
- **🏠 Housing** - Rent, maintenance, home supplies
- **📦 Other** - Miscellaneous expenses

## 🔧 Project Structure

```
expense-tracker-ai/
├── components/                # React components
│   ├── Dashboard.tsx         # Analytics dashboard
│   ├── ExpenseList.tsx       # Recent expenses list
│   ├── ReceiptProcessorModal.tsx # AI receipt processing
│   └── icons/                # SVG icon components
├── hooks/                    # Custom React hooks
│   └── useLocalStorage.ts    # Local storage management
├── services/                 # External service integrations
│   └── geminiService.ts      # Gemini AI API integration
├── utils/                    # Utility functions
│   └── fileUtils.ts          # File processing utilities
├── types.ts                  # TypeScript type definitions
├── App.tsx                   # Main application component
└── index.tsx                 # Application entry point
```

## 🌟 Key Features Explained

### AI-Powered Receipt Processing
The app uses Google Gemini's vision capabilities to:
- Recognize text in receipt images using OCR
- Extract structured data from unstructured receipt layouts
- Identify individual line items and their prices
- Suggest appropriate expense categories

### Local Data Storage
- All expense data is stored locally in your browser
- No server required - works completely offline after initial load
- Data persists between sessions
- Privacy-focused approach - your data never leaves your device

### Visual Analytics
- Interactive charts show spending trends over time
- Category-based breakdowns help identify spending patterns
- Multiple time views provide different perspectives on your expenses
- Responsive design ensures charts work on all screen sizes

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Deploy to Vercel
1. Connect your GitHub repository to Vercel
2. Set the `GEMINI_API_KEY` environment variable in Vercel dashboard
3. Deploy automatically on push to main branch

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful receipt processing capabilities
- **React & TypeScript** for robust frontend development
- **Recharts** for beautiful data visualizations
- **Vite** for fast development experience

---

<div align="center">
Made with ❤️ by <a href="https://github.com/lyven81">lyven81</a>
</div>
