# 🎨 AI Photo Editor

[![React](https://img.shields.io/badge/React-18.0-blue?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-4.0-purple?logo=vite)](https://vitejs.dev/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI-orange?logo=google)](https://ai.google.dev/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=vercel)](https://ai.studio/apps/drive/1hMVXOco72bBp0FcxZsosL82lAV7y1_Wh)

Professional-grade AI-powered photo editing application with intelligent enhancement features, real-time filters, and modern responsive design.

<div align="center">
<img width="1200" height="475" alt="AI Photo Editor Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

## 🚀 Live Demo

**[🌟 View Live Demo](https://ai.studio/apps/drive/1hMVXOco72bBp0FcxZsosL82lAV7y1_Wh)** | [📹 Video Demo](#)

## ✨ Features

- **🤖 AI-Powered Enhancement:** Intelligent photo optimization using Google's Gemini AI
- **🎨 Real-time Filters:** Apply and preview filters instantly with live updates
- **📱 Responsive Design:** Seamless experience across desktop, tablet, and mobile devices
- **⚡ Fast Processing:** Optimized performance with Vite build system
- **🎯 Intuitive UI:** Modern, user-friendly interface with TypeScript reliability
- **💾 Export Options:** Download enhanced photos in multiple formats
- **🔧 Advanced Controls:** Fine-tune adjustments with professional-grade tools

## 🛠️ Tech Stack

**Frontend Framework:**
- **React 18** - Latest React with concurrent features
- **TypeScript 5.0** - Type-safe development with latest features
- **Vite 4.0** - Lightning-fast build tool and dev server

**AI Integration:**
- **Google Gemini API** - Advanced AI photo enhancement
- **Computer Vision APIs** - Image processing and analysis

**Styling & UI:**
- **CSS3/Modern Styling** - Responsive design with advanced CSS features
- **Component Architecture** - Modular, reusable UI components

**Development Tools:**
- **ESLint** - Code quality and consistency
- **Prettier** - Automatic code formatting
- **TypeScript Strict Mode** - Enhanced type safety

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** (LTS recommended)
- **npm** or **yarn** package manager
- **Gemini API Key** from Google AI Studio

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-photo-editor.git
cd ai-photo-editor

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Add your Gemini API key to .env.local

# Start development server
npm run dev
```

### Environment Configuration

Create a `.env.local` file in the root directory:

```env
# Required: Google Gemini AI API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Development configuration
VITE_APP_NAME=AI Photo Editor
VITE_NODE_ENV=development
```

## 📖 Usage

### Basic Photo Editing
1. **Upload Photo:** Drag and drop or click to select image files
2. **Apply AI Enhancement:** Use the AI-powered auto-enhance feature
3. **Fine-tune Settings:** Adjust brightness, contrast, saturation, and more
4. **Preview Changes:** See real-time updates as you make adjustments
5. **Export Result:** Download your enhanced photo in preferred format

### Advanced Features
- **Batch Processing:** Edit multiple photos simultaneously
- **Custom Presets:** Save and reuse your favorite editing configurations
- **History Management:** Undo/redo changes with full edit history
- **Format Support:** Works with JPG, PNG, WEBP, and more formats

## 📁 Project Structure

```
ai-photo-editor/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Editor/         # Photo editor components
│   │   ├── Controls/       # Editing control panels
│   │   └── Common/         # Shared components
│   ├── services/           # API integration and services
│   │   ├── gemini.ts      # Gemini AI service
│   │   └── imageProcessor.ts
│   ├── utils/              # Helper functions
│   ├── types/              # TypeScript type definitions
│   └── App.tsx            # Main application component
├── public/                 # Static assets
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite build configuration
└── README.md
```

## 🧪 Testing & Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🚀 Deployment

### Netlify/Vercel Deployment
1. Build the project: `npm run build`
2. Deploy the `dist` folder to your preferred platform
3. Set environment variables in deployment settings
4. Configure build command: `npm run build`
5. Set publish directory: `dist`

### Manual Deployment
```bash
# Build optimized production bundle
npm run build

# Serve locally to test
npm run preview

# Deploy dist/ folder to your hosting platform
```

## 🎯 Performance Features

- **Code Splitting:** Automatic bundle optimization
- **Lazy Loading:** Components loaded on demand
- **Image Optimization:** Efficient image processing and caching
- **PWA Ready:** Installable progressive web app capabilities

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI Team** for the powerful Gemini API
- **React Community** for the amazing ecosystem
- **Vite Team** for the excellent build tool
- **TypeScript Team** for enhanced developer experience

## 📧 Contact

- **Portfolio:** [View More Projects](../../README.md)
- **Issues:** [Report Bugs](https://github.com/yourusername/ai-photo-editor/issues)
- **Discussions:** [Feature Requests](https://github.com/yourusername/ai-photo-editor/discussions)

---

⭐ **If you found this project helpful, please give it a star!** ⭐

*Built with ❤️ using React, TypeScript, and AI*