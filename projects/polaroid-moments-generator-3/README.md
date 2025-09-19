# 📸 Polaroid Moments Generator 3

[![React](https://img.shields.io/badge/React-19.1+-blue?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue?logo=typescript)](https://typescriptlang.org/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange?logo=google)](https://ai.google.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.2+-purple?logo=vite)](https://vitejs.dev/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=vercel)](https://ai.studio/apps/drive/1PDCCItpHmR0x7tjJOA0jQ8V9lp3pVOXu)

Create nostalgic retro-style group photos from three individual images using advanced AI technology. Generate compelling visual stories featuring three people with dynamic poses and authentic group interactions.

<div align="center">
<img width="1200" height="475" alt="Polaroid Moments Generator 3 Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

## 🚀 Live Demo

**[🌟 View Live Demo](https://ai.studio/apps/drive/1PDCCItpHmR0x7tjJOA0jQ8V9lp3pVOXu)** | [📹 Video Demo](#)

## ✨ Features

- **🎭 Three-Person Group Generation:** Advanced AI composition for authentic group dynamics
- **📸 Four Unique Story Poses:** Victory Shout, Whispering Secrets, Celebration, and Mixed Reactions
- **🤖 AI-Powered Storytelling:** Each pose creates a compelling narrative moment
- **🎨 Vintage Polaroid Aesthetic:** Authentic retro styling with classic polaroid frames
- **⚡ Advanced Image Processing:** Seamless blending of three separate images
- **📱 Modern React Interface:** Clean, responsive design with dark/light theme support
- **🔒 Secure Processing:** No permanent data storage, privacy-focused approach
- **🎯 Professional Quality:** High-resolution outputs suitable for printing and sharing

## 🛠️ Tech Stack

**Frontend Framework:**
- **React 19.1+** - Latest React with modern features
- **TypeScript 5.8+** - Type-safe development
- **Vite 6.2+** - Fast build tool and dev server

**AI & Image Processing:**
- **Google Gemini AI** - Advanced multi-image composition and generation
- **Custom Image Processing** - Base64 encoding and optimization
- **Smart Pose Synthesis** - AI-driven group dynamics and positioning

**Styling & UX:**
- **Tailwind CSS** - Utility-first CSS framework
- **Custom Components** - Reusable UI components for three-image upload
- **Responsive Design** - Mobile-first approach with seamless UX

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+**
- **Gemini API Key** from Google AI Studio

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lyven81/ai-project.git
   cd ai-project/projects/polaroid-moments-generator-3
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

### 1. Three-Image Upload
- Upload three separate photos featuring different people
- Each image should contain a clear view of the person's face and body
- AI automatically processes and prepares images for composition

### 2. AI Group Composition
- Gemini AI analyzes facial features, body positions, and lighting
- Intelligently blends three people into cohesive group scenarios
- Maintains individual identity while creating natural group dynamics

### 3. Story-Driven Pose Generation
- **Victory Shout:** Triumphant celebration with raised fists and excited expressions
- **Whispering a Secret:** Intimate storytelling moment with one person sharing secrets
- **Celebration Pose:** Classic group shot with arms around shoulders showing camaraderie
- **Mixed Reactions:** Playful scene with contrasting expressions and gestures

### 4. Vintage Polaroid Processing
- Applies authentic retro styling and color grading
- Adds classic polaroid frame and aesthetic elements
- Optimizes for both digital viewing and physical printing

## 🎯 Pose Descriptions

### Victory Shout
Three friends stand side by side with fists clenched and faces lit with excitement, capturing the energy of a shared victory moment with wide smiles and triumphant poses.

### Whispering a Secret
Two friends lean in for an intimate conversation while the third looks at the camera with curious amusement, creating a fun storytelling dynamic within the photo.

### Celebration Pose
Classic group shot with arms around shoulders, radiating joy and camaraderie. One friend playfully points toward the middle person, highlighting the celebratory mood.

### Mixed Reactions
Contrasting poses showing different personalities - one puzzled, one confident with crossed arms, and one gesturing in surprise, creating a playful disagreement scene.

## 🔧 Project Structure

```
polaroid-moments-generator-3/
├── components/                # React components
│   ├── ImageUploader.tsx     # Three-image upload interface
│   ├── ImageGrid.tsx         # Generated polaroid display
│   ├── Loader.tsx            # Loading animation
│   └── PolaroidFrame.tsx     # Vintage styling component
├── services/                 # External service integrations
│   └── geminiService.ts      # Gemini AI API integration
├── constants.ts              # Pose prompts and configurations
├── App.tsx                   # Main application component
└── index.tsx                 # Application entry point
```

## 🌟 Key Features Explained

### Advanced Three-Person Composition
The app uses sophisticated AI algorithms to:
- Analyze spatial relationships between three people
- Create natural group dynamics and interactions
- Maintain individual facial features and characteristics
- Generate realistic lighting and shadow effects

### Story-Driven Photography
Each pose tells a specific story:
- **Emotional narratives** that resonate with viewers
- **Dynamic interactions** between group members
- **Authentic moments** that feel candid and natural
- **Versatile scenarios** suitable for different relationships

### Professional Quality Output
- **High-resolution generation** for printing and sharing
- **Authentic vintage aesthetic** with period-appropriate styling
- **Optimized file sizes** for web and mobile viewing
- **Multiple format support** for various use cases

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Deploy to Google AI Studio
1. Connect your project to Google AI Studio
2. Set the `GEMINI_API_KEY` environment variable
3. Deploy automatically with integrated build process

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced multi-image composition capabilities
- **React & TypeScript** for robust frontend development
- **Vite** for fast development experience
- **Vintage Photography Community** for aesthetic inspiration

---

<div align="center">
Made with ❤️ by <a href="https://github.com/lyven81">lyven81</a>
</div>
