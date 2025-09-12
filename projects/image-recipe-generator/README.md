# AI Recipe Generator

A web app that analyzes photos of food ingredients and generates creative, personalized recipes using Claude AI. Upload a photo of items in your fridge, basket, or on a table, and get tailored step-by-step recipes based on your cuisine preferences and cooking skill level.

## Features

- Photo analysis of food ingredients using AI vision
- Creative recipe generation powered by Claude AI
- Customizable cuisine styles (Italian, Asian, Mexican, etc.)
- Adjustable cooking difficulty levels (Beginner, Intermediate, Advanced)
- Step-by-step recipe instructions
- Ingredient substitution suggestions

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn anthropic python-dotenv pydantic pillow
   ```

2. **Set up environment**:
   ```bash
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
   Or copy `.env` file and update the API key.

3. **Run the server**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```

4. **Test the app**:
   - Health check: `GET http://localhost:8080/healthz`
   - API docs: `GET http://localhost:8080/docs`
   - Upload photo: `POST http://localhost:8080/analyze-recipe`
   - Web interface: `GET http://localhost:8080/`

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t recipe-generator .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 8080:8080 -e ANTHROPIC_API_KEY=your_api_key recipe-generator
   ```

### Cloud Run Deployment

1. **Build and push**:
   ```bash
   gcloud builds submit --tag asia.gcr.io/PROJECT_ID/recipe-generator
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy recipe-generator \
     --image asia.gcr.io/PROJECT_ID/recipe-generator \
     --set-env-vars ANTHROPIC_API_KEY=your_api_key \
     --allow-unauthenticated
   ```

## API Usage

### POST /analyze-recipe

Request body (multipart form data):
- `image`: Image file of food ingredients
- `cuisine_style`: Preferred cuisine (e.g., "Italian", "Asian", "Mexican")
- `cooking_level`: Difficulty level ("Beginner", "Intermediate", "Advanced")
- `dietary_restrictions`: Optional dietary restrictions

Response:
```json
{
  "recipe_name": "Mediterranean Pasta Primavera",
  "ingredients": ["tomatoes", "basil", "olive oil", "pasta"],
  "instructions": ["Step 1...", "Step 2..."],
  "prep_time": "15 minutes",
  "cook_time": "20 minutes",
  "servings": 4,
  "difficulty": "Beginner"
}
```

## Environment Variables

- `ANTHROPIC_API_KEY` (required): Your Anthropic Claude API key
- `PORT` (optional): Server port, defaults to 8080

## License

MIT License