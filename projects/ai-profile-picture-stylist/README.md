# AI Profile Picture Stylist

## Overview
An AI-powered application that transforms a single uploaded photo into four distinct, professional profile images using Google's Gemini AI. Perfect for creating professional headshots for LinkedIn, corporate websites, and social media platforms.

## Features
- **Smart Image Analysis**: Automatically detects and validates 1-2 people in uploaded photos
- **Four Professional Styles**: Generates images in Classic Black & White, Corporate Executive, Natural Lifestyle, and Modern Editorial styles
- **Real-time Processing**: Uses Google Gemini AI for high-quality image transformations
- **Responsive Design**: Clean, modern interface built with React and Tailwind CSS
- **Download Ready**: All generated images are ready for immediate download and use

## Tech Stack
- **Frontend**: React 19 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **AI Integration**: Google Gemini API (@google/genai)
- **Image Processing**: Base64 encoding for seamless AI processing

## Project Structure
```
ai-profile-picture-stylist/
├── src/
│   ├── App.tsx                    # Main application component
│   ├── components/
│   │   ├── Header.tsx             # Application header
│   │   ├── Footer.tsx             # Application footer
│   │   ├── ImageUploader.tsx      # File upload component
│   │   ├── ImageGrid.tsx          # Generated images display
│   │   ├── Loader.tsx             # Loading animation
│   │   ├── StyleCard.tsx          # Individual style image card
│   │   └── icons/                 # Icon components
│   ├── services/
│   │   └── geminiService.ts       # Google Gemini AI integration
│   ├── constants.ts               # Application constants
│   └── types.ts                   # TypeScript type definitions
├── deployment/
│   ├── Dockerfile                 # Docker configuration
│   ├── cloudbuild.yaml           # Google Cloud Build
│   └── deploy.sh                 # Deployment script
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── index.tsx
└── README.md
```

## Installation & Setup

### Prerequisites
- Node.js (version 18+)
- Google Gemini API key

### Local Development
1. **Clone the repository**:
   ```bash
   git clone https://github.com/lyven81/ai-project.git
   cd ai-project/projects/ai-profile-picture-stylist
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create a `.env.local` file in the root directory:
   ```
   VITE_GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

5. **Open your browser** and navigate to `http://localhost:5173`

## Usage
1. **Upload a Photo**: Click to upload or drag & drop an image containing 1-2 people
2. **Image Validation**: The app automatically verifies the image contains the right number of people
3. **Generate Styles**: Click "Generate Styles" to create four professional variations
4. **Download Results**: Save any or all of the generated professional profile pictures

## Generated Styles
- **Classic Black & White**: Timeless, sophisticated monochrome styling
- **Corporate Executive**: Professional business headshot appearance
- **Natural Lifestyle**: Warm, approachable lifestyle photography look
- **Modern Editorial**: Contemporary, artistic portrait styling

## API Integration
The application integrates with Google's Gemini AI through:
- **Image Analysis**: Counts people in uploaded photos for validation
- **Style Generation**: Creates four distinct professional styles using AI prompts
- **Error Handling**: Robust error management for API failures

## Deployment
The project includes deployment configurations for:
- **Google Cloud Run**: Serverless container deployment
- **Docker**: Containerized application
- **Netlify**: Static site deployment

### Google Cloud Deployment
```bash
# Build and deploy using Google Cloud Build
gcloud builds submit --config deployment/cloudbuild.yaml

# Or use the deployment script
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

## Performance Considerations
- **Image Optimization**: Efficient base64 encoding for AI processing
- **Error Boundaries**: Comprehensive error handling for API failures
- **Loading States**: Clear feedback during image generation
- **Responsive Design**: Optimized for mobile and desktop viewing

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is part of the AI Project Portfolio. See the main repository for licensing information.

## Support
For issues, questions, or contributions, please visit the [main AI Project repository](https://github.com/lyven81/ai-project).