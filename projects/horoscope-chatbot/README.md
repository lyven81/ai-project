# Aster — Horoscope Chatbot

A FastAPI-based horoscope chatbot powered by Claude AI that provides personalized astrological guidance.

## Features

- Natural horoscope readings based on zodiac signs or birth dates
- RESTful API with FastAPI
- Docker containerization ready
- Health check endpoint
- Support for multiple date formats

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn anthropic python-dotenv pydantic
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

4. **Test the API**:
   - Health check: `GET http://localhost:8080/healthz`
   - API docs: `GET http://localhost:8080/docs`
   - Get reading: `POST http://localhost:8080/reading`

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t horoscope-chatbot .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 8080:8080 -e ANTHROPIC_API_KEY=your_api_key horoscope-chatbot
   ```

### Cloud Run Deployment

1. **Build and push**:
   ```bash
   gcloud builds submit --tag asia.gcr.io/PROJECT_ID/horoscope-chatbot
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy horoscope-chatbot \
     --image asia.gcr.io/PROJECT_ID/horoscope-chatbot \
     --set-env-vars ANTHROPIC_API_KEY=your_api_key \
     --allow-unauthenticated
   ```

## API Usage

### POST /reading

Request body:
```json
{
  "message": "How's my day looking?",
  "zodiac": "Leo",
  "birthdate": "1990-08-15"
}
```

Response:
```json
{
  "answer": "Your horoscope reading...",
  "used_profile": {
    "zodiac": "Leo",
    "birthdate": "1990-08-15"
  }
}
```

## Environment Variables

- `ANTHROPIC_API_KEY` (required): Your Anthropic Claude API key
- `PORT` (optional): Server port, defaults to 8080

## License

MIT License