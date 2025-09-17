# 🎨 AI Photo Editor

[![React](https://img.shields.io/badge/React-18.0-blue?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-4.0-purple?logo=vite)](https://vitejs.dev/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI-orange?logo=google)](https://ai.google.dev/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=vercel)](https://ai.studio/apps/drive/1hMVXOco72bBp0FcxZsosL82lAV7y1_Wh)

Professional-grade AI-powered photo editing application with intelligent enhancement features, advanced filters, and modern responsive design. Transform your photos with cutting-edge computer vision technology and intuitive editing tools.

<div align="center">
<img width="1200" height="475" alt="AI Photo Editor Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

## 🚀 Live Demo

**[🌟 View Live Demo](https://ai.studio/apps/drive/1hMVXOco72bBp0FcxZsosL82lAV7y1_Wh)** | [📹 Video Demo](#)

## ✨ Features

- **🤖 AI-Powered Enhancement:** Intelligent photo optimization using Google's Gemini AI for automatic improvement
- **🎨 Real-time Filters:** Apply and preview artistic filters instantly with live updates and zero lag
- **🖼️ Advanced Photo Processing:** Professional-grade editing tools with precise color and exposure control
- **📱 Responsive Design:** Seamless experience across desktop, tablet, and mobile devices
- **⚡ Lightning-Fast Performance:** Optimized processing with Vite build system and efficient algorithms
- **🎯 Intuitive Interface:** Modern, user-friendly design with TypeScript reliability and accessibility
- **💾 Multi-Format Export:** Download enhanced photos in JPG, PNG, WEBP, and other formats
- **🔧 Professional Controls:** Fine-tune brightness, contrast, saturation, and advanced parameters
- **📊 Batch Processing:** Edit multiple photos simultaneously with consistent settings
- **🎭 Custom Presets:** Save and reuse your favorite editing configurations
- **↩️ Non-Destructive Editing:** Full undo/redo history with original image preservation

## 🛠️ Tech Stack

**Frontend Framework:**
- **React 18** - Latest React with concurrent features and hooks
- **TypeScript 5.0** - Type-safe development with enhanced IDE support
- **Vite 4.0** - Lightning-fast build tool and development server

**AI & Computer Vision:**
- **Google Gemini API** - Advanced AI photo enhancement and analysis
- **Canvas API** - High-performance image manipulation and rendering
- **Web Workers** - Background processing for smooth UI performance
- **WebGL** - GPU-accelerated image processing for advanced filters

**Image Processing:**
- **HTML5 Canvas** - Direct pixel manipulation and real-time editing
- **File API** - Drag-and-drop file handling and image loading
- **Image Optimization** - Automatic compression and format conversion
- **Color Space Management** - Professional color accuracy and profiles

**Performance & Architecture:**
- **Component Architecture** - Modular, reusable UI components
- **State Management** - Efficient React state with hooks and context
- **Lazy Loading** - On-demand component and resource loading
- **Progressive Web App** - Installable with offline capabilities

**Development Tools:**
- **ESLint** - Code quality and consistency enforcement
- **Prettier** - Automatic code formatting and style consistency
- **TypeScript Strict Mode** - Enhanced type safety and error prevention

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** (LTS recommended)
- **npm** or **yarn** package manager
- **Gemini API Key** from Google AI Studio
- **Modern browser** with Canvas and WebGL support

### Installation

```bash
# Clone the repository
git clone https://github.com/lyven81/ai-project.git
cd ai-project/projects/ai-photo-editor

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

# Optional: Application configuration
VITE_APP_NAME=AI Photo Editor
VITE_NODE_ENV=development
VITE_MAX_FILE_SIZE=10485760
VITE_SUPPORTED_FORMATS=jpg,jpeg,png,webp,bmp

# Performance settings
VITE_CANVAS_MAX_WIDTH=4096
VITE_CANVAS_MAX_HEIGHT=4096
VITE_WEBGL_ENABLED=true
```

## 📖 Usage

### Basic Photo Editing
1. **Upload Photo:** Drag and drop or click to select image files (up to 10MB)
2. **AI Auto-Enhancement:** Use intelligent one-click optimization with Gemini AI
3. **Manual Adjustments:** Fine-tune brightness, contrast, saturation, and color balance
4. **Apply Filters:** Choose from artistic, vintage, and professional filter presets
5. **Real-time Preview:** See instant updates as you make adjustments
6. **Export & Download:** Save your enhanced photo in multiple high-quality formats

### Advanced Photo Processing
- **Professional Tools:** Curves, levels, HSV adjustment, and color grading
- **Selective Editing:** Target specific areas or colors for precise enhancement
- **Noise Reduction:** AI-powered image denoising and sharpening
- **Format Conversion:** Convert between JPG, PNG, WEBP, and other formats
- **Batch Processing:** Apply consistent edits to multiple photos simultaneously
- **Custom Presets:** Save and share your favorite editing configurations

### AI Enhancement Features
- **Smart Auto-Enhance:** Intelligent optimization based on image content analysis
- **Scene Recognition:** Automatic adjustments for portraits, landscapes, and objects
- **Color Correction:** AI-powered white balance and color temperature optimization
- **Detail Enhancement:** Intelligent sharpening without artifacts or over-processing

## 📁 Project Structure

```
ai-photo-editor/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Editor/         # Core photo editor components
│   │   │   ├── Canvas/     # Image canvas and viewport
│   │   │   ├── Toolbar/    # Editing tools and controls
│   │   │   └── Filters/    # Filter preview and application
│   │   ├── Controls/       # Editing control panels
│   │   │   ├── Basic/      # Brightness, contrast, saturation
│   │   │   ├── Advanced/   # Curves, levels, color grading
│   │   │   └── AI/         # AI enhancement controls
│   │   ├── Upload/         # File upload and drag-drop
│   │   ├── Export/         # Save and download functionality
│   │   └── Common/         # Shared UI components
│   ├── services/           # API integration and services
│   │   ├── geminiAI.ts     # Gemini AI integration
│   │   ├── imageProcessor.ts # Core image processing
│   │   ├── filterEngine.ts # Filter application engine
│   │   └── exportService.ts # File export handling
│   ├── utils/              # Helper functions
│   │   ├── imageUtils.ts   # Image manipulation utilities
│   │   ├── colorUtils.ts   # Color space conversions
│   │   ├── canvasUtils.ts  # Canvas operations
│   │   └── formatUtils.ts  # File format handling
│   ├── types/              # TypeScript type definitions
│   │   ├── image.ts        # Image-related types
│   │   ├── filters.ts      # Filter and effect types
│   │   └── editor.ts       # Editor state types
│   ├── hooks/              # Custom React hooks
│   │   ├── useCanvas.ts    # Canvas management
│   │   ├── useImage.ts     # Image state management
│   │   └── useHistory.ts   # Undo/redo functionality
│   ├── styles/             # CSS and styling
│   │   ├── components/     # Component-specific styles
│   │   └── globals.css     # Global styles and variables
│   └── App.tsx            # Main application component
├── public/                 # Static assets
│   ├── presets/           # Default filter presets
│   └── icons/             # UI icons and graphics
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── vite.config.ts         # Vite build configuration
└── README.md
```

## 🎨 AI Photo Processing Capabilities

### Intelligent Enhancement Engine
- **Scene Analysis:** Automatic detection of photo type (portrait, landscape, macro, etc.)
- **Content-Aware Processing:** AI adjustments based on image content and composition
- **Smart Color Correction:** Intelligent white balance and color temperature optimization
- **Adaptive Sharpening:** Context-sensitive detail enhancement without artifacts

### Advanced Filter Technology
- **Real-time Processing:** WebGL-accelerated filters with 60fps performance
- **Professional Presets:** Curated filter collections for different photography styles
- **Custom Filter Creation:** Build and save your own unique filter combinations
- **Batch Filter Application:** Apply consistent effects across multiple images

### Performance Optimization
- **GPU Acceleration:** WebGL-based processing for complex operations
- **Worker Threads:** Background processing to maintain responsive UI
- **Memory Management:** Efficient handling of large image files
- **Progressive Loading:** Smooth experience with high-resolution images

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

### Netlify/Vercel Deployment (Recommended)
1. Build the project: `npm run build`
2. Deploy the `dist` folder to your preferred platform
3. Set `GEMINI_API_KEY` in environment variables
4. Configure build settings:
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Node version: 16+

### Docker Deployment
```bash
# Build Docker image
docker build -t ai-photo-editor .

# Run container with environment variables
docker run -p 3000:3000 -e GEMINI_API_KEY=your_key ai-photo-editor
```

### Manual Static Hosting
```bash
# Build optimized production bundle
npm run build

# Test production build locally
npm run preview

# Deploy dist/ folder to any static hosting platform
# Ensure HTTPS for secure operation
```

## 📊 Performance Metrics

- **Processing Speed:** Sub-second filter application with WebGL acceleration
- **File Support:** Images up to 10MB in JPG, PNG, WEBP, BMP formats
- **Render Performance:** 60fps real-time preview with smooth interactions
- **Memory Efficiency:** Optimized Canvas operations for large images
- **Browser Compatibility:** Works on all modern browsers with WebGL support
- **Mobile Performance:** Responsive design optimized for touch devices

## 🔒 Privacy & Security

- **Local Processing:** All image editing happens client-side in your browser
- **No Image Storage:** Photos are never uploaded or stored on external servers
- **Privacy First:** No data collection, tracking, or analytics
- **Secure APIs:** Encrypted communications with Gemini AI for enhancement features
- **Open Source:** Transparent codebase with no hidden functionality

## 🎯 Use Cases

- **Photography Enhancement:** Professional photo editing for photographers and content creators
- **Social Media Optimization:** Quick enhancement and filtering for social platforms
- **E-commerce Product Photos:** Consistent, high-quality product image editing
- **Personal Photo Management:** Organize and enhance family photos and memories
- **Educational Projects:** Learn photo editing techniques with professional tools
- **Creative Exploration:** Experiment with artistic filters and effects

## 🤝 Contributing

We welcome contributions! Areas for improvement:

- **New Filter Effects:** Creative and artistic filter development
- **AI Enhancement Features:** Advanced machine learning capabilities
- **Performance Optimization:** Faster processing and better memory management
- **Mobile Experience:** Enhanced touch controls and mobile-specific features

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-filters`)
3. Set up development environment with Node.js 16+
4. Install dependencies and configure Gemini API
5. Make your changes with proper testing
6. Submit a pull request with detailed description

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google AI Team** for the powerful Gemini API and computer vision capabilities
- **React Community** for the amazing ecosystem and component libraries
- **Vite Team** for the excellent build tool and development experience
- **TypeScript Team** for enhanced developer experience and type safety
- **WebGL Community** for GPU acceleration standards and optimization techniques

## 📧 Contact

- **Portfolio:** [View More Projects](../../README.md)
- **Issues:** [Report Bugs](https://github.com/lyven81/ai-project/issues)
- **Discussions:** [Feature Requests](https://github.com/lyven81/ai-project/discussions)

---

⭐ **If you found this project helpful, please give it a star!** ⭐

*Transform your photos with professional AI-powered editing tools* 🎨✨