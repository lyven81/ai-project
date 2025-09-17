# AI Background Changer

## 🎯 Project Overview

AI Background Changer is an intelligent web application that uses Google Gemini AI to seamlessly replace and modify image backgrounds through natural language prompts. Users can upload any image and describe their desired background changes in plain English, and the AI will generate a new version with the requested modifications while preserving the main subject.

## ✨ Key Features

- **Smart Background Replacement**: AI-powered background editing using Google Gemini 2.5 Flash Image Preview
- **Natural Language Interface**: Describe background changes in plain English
- **Real-time Processing**: Instant image generation with visual feedback
- **Drag & Drop Upload**: Intuitive image upload interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Error Handling**: Comprehensive error management and user feedback

## 🛠️ Tech Stack

### Frontend
- **React 19**: Latest React with hooks and modern features
- **TypeScript 5.8**: Type-safe development
- **Vite 6.2**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-first approach

### AI & Backend
- **Google Gemini AI**: Gemini 2.5 Flash Image Preview model
- **Multimodal Processing**: Text and image understanding
- **Base64 Image Handling**: Efficient image processing
- **Real-time API Integration**: Seamless AI communication

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ (LTS recommended)
- Gemini API key from Google AI Studio
- Modern web browser with camera/file access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lyven81/ai-project.git
   cd ai-project/projects/ai-background-changer
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Environment setup**
   ```bash
   cp .env.example .env.local
   ```
   Add your Gemini API key to `.env.local`:
   ```
   API_KEY=your_gemini_api_key_here
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

5. **Build for production**
   ```bash
   npm run build
   ```

## 📁 Project Structure

```
ai-background-changer/
├── src/
│   ├── App.tsx                 # Main application component
│   ├── types.ts               # TypeScript type definitions
│   ├── components/            # React components
│   │   ├── ImageUploader.tsx  # File upload component
│   │   ├── PromptInput.tsx    # Text input for prompts
│   │   ├── GeneratedImage.tsx # Result display component
│   │   ├── Loader.tsx         # Loading animation
│   │   └── Icons.tsx          # SVG icon components
│   ├── services/              # API and external services
│   │   └── geminiService.ts   # Gemini AI integration
│   └── utils/                 # Utility functions
│       └── imageUtils.ts      # Image processing helpers
├── deployment/                # Deployment configurations
├── package.json              # Dependencies and scripts
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── index.html                # HTML entry point
└── README.md                 # Project documentation
```

## 🎨 How It Works

1. **Image Upload**: Users drag and drop or select an image file
2. **Prompt Input**: Describe the desired background change in natural language
3. **AI Processing**: Gemini AI analyzes the image and prompt
4. **Background Generation**: AI generates a new image with modified background
5. **Result Display**: Show the original and generated images side by side

## 🔧 Core Components

### ImageUploader Component
- Drag and drop file upload
- Image preview functionality
- File type validation
- Error handling for invalid files

### PromptInput Component
- Natural language text input
- Real-time validation
- Disabled state during processing
- Placeholder suggestions

### GeneratedImage Component
- Display generated results
- Image comparison view
- Download functionality
- Error state handling

### Gemini Service
- API key management
- Image to base64 conversion
- Multimodal API calls
- Response processing

## 🌐 API Integration

The application integrates with Google Gemini AI API:

```typescript
const response = await ai.models.generateContent({
  model: 'gemini-2.5-flash-image-preview',
  contents: {
    parts: [imagePart, textPart],
  },
  config: {
    responseModalities: [Modality.IMAGE, Modality.TEXT],
  },
});
```

## 🚀 Deployment Options

### Local Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
npm run preview
```

### Docker Deployment
```bash
docker build -t ai-background-changer .
docker run -p 3000:3000 ai-background-changer
```

### Cloud Deployment
- **Netlify**: Static site deployment
- **Vercel**: Serverless deployment
- **Google Cloud Run**: Containerized deployment

## 🔍 Use Cases

- **Photo Editing**: Professional background replacement
- **E-commerce**: Product photography enhancement
- **Social Media**: Creative content generation
- **Marketing**: Brand-consistent visuals
- **Personal Projects**: Family photo enhancement

## 🎯 Performance Features

- **Optimized Bundle**: Code splitting and lazy loading
- **Fast Loading**: Vite's optimized build process
- **Memory Management**: Efficient image handling
- **Error Recovery**: Graceful failure handling
- **Mobile Responsive**: Touch-friendly interface

## 📊 Technical Specifications

- **Image Formats**: JPEG, PNG, WebP
- **Max File Size**: 10MB (configurable)
- **Processing Time**: 2-10 seconds (depending on complexity)
- **Browser Support**: Modern browsers with ES2020+
- **API Rate Limits**: Managed through error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI Project Portfolio and follows the same licensing terms.

## 🔗 Links

- **Live Demo**: [Coming Soon]
- **Portfolio**: [AI Project Portfolio](https://github.com/lyven81/ai-project)
- **Documentation**: [Full Docs](https://github.com/lyven81/ai-project/blob/main/README.md)

---

Built with ❤️ using React, TypeScript, and Google Gemini AI