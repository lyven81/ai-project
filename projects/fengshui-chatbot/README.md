# 風水顧問 — Fengshui Chatbot

A FastAPI-based professional fengshui consultation chatbot powered by Claude AI that provides personalized guidance based on traditional Chinese fengshui principles and five-element theory.

## Features

- **Professional Fengshui Consultation**: Expert guidance based on five elements (木火土金水)
- **Five Element Analysis**: Personalized advice using Wood, Fire, Earth, Metal, Water element theory
- **Bagua Integration**: Directional guidance using traditional eight trigrams
- **Element Harmony Calculation**: Compatibility analysis between different elements
- **Seasonal Energy Reading**: Time-based recommendations aligned with natural cycles
- **RESTful API**: Built with FastAPI for easy integration
- **Docker Ready**: Complete containerization support
- **Bilingual Support**: Chinese interface with English documentation

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
   Or create a `.env` file with your API key.

3. **Run the server**:
   ```bash
   python app.py
   ```
   Or:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```

4. **Test the API**:
   - Health check: `GET http://localhost:8080/healthz`
   - API docs: `GET http://localhost:8080/docs`
   - Web interface: `GET http://localhost:8080/`
   - Chat endpoint: `POST http://localhost:8080/chat`

### Docker Deployment

1. **Build the image**:
   ```bash
   docker build -t fengshui-chatbot .
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 8080:8080 -e ANTHROPIC_API_KEY=your_api_key fengshui-chatbot
   ```

### Cloud Run Deployment

1. **Build and push**:
   ```bash
   gcloud builds submit --tag asia.gcr.io/PROJECT_ID/fengshui-chatbot
   ```

2. **Deploy**:
   ```bash
   gcloud run deploy fengshui-chatbot \
     --image asia.gcr.io/PROJECT_ID/fengshui-chatbot \
     --set-env-vars ANTHROPIC_API_KEY=your_api_key \
     --allow-unauthenticated
   ```

## API Usage

### POST /chat

Request body:
```json
{
  "user": "張三",
  "element": "木",
  "question": "我最近工作上遇到困難，該如何改善？",
  "category": "事業",
  "timeframe": "本週",
  "partner_element": "火",
  "home_direction": "東南"
}
```

Response:
```json
{
  "title": "木元素本週深度風水解析",
  "reply": "【當日五行】當日水元素為木元素帶來生機勃勃的能量流動...",
  "fengshui_reasoning": "基於木元素特質與環境的專業分析",
  "tips": [
    "善用木元素的天賦特質",
    "在清晨5-7時時段行動最有利",
    "保持木元素的內在平衡",
    "順應天時地利，創造和諧環境"
  ],
  "timing_advice": "配合春季季節能量，在3日前後行動最為順利",
  "affirmation": "我是充滿木能量的人，與天地和諧共振",
  "lucky_elements": {
    "color": "綠色",
    "number": 3,
    "direction": "東方",
    "time": "清晨5-7時",
    "element": "木",
    "season": "春季"
  },
  "fengshui_insight": {
    "daily_element_influence": "當日水元素為木元素帶來穩定能量",
    "seasonal_energy": "春季成長能量，適合新開始和創新",
    "element_guidance": "木元素在此時期特別適合發揮生機的特質",
    "bagua_guidance": "關注東方方位的能量流動，有助於提升整體運勢",
    "element_harmony_note": "與火的五行和諧度：80%"
  },
  "timeframe": "本週",
  "harmony_score": 80
}
```

## Five Elements (五行)

The chatbot supports analysis based on traditional Chinese five elements:

- **木 (Wood)**: Growth, creativity, spring energy, east direction
- **火 (Fire)**: Passion, energy, summer season, south direction  
- **土 (Earth)**: Stability, nurturing, late summer, center
- **金 (Metal)**: Structure, precision, autumn, west direction
- **水 (Water)**: Wisdom, flow, winter season, north direction

## Supported Categories

- **感情** (Love/Relationships)
- **事業** (Career)
- **健康** (Health)
- **財運** (Finance)
- **居家環境** (Home Environment)
- **綜合** (General)

## Environment Variables

- `ANTHROPIC_API_KEY` (required): Your Anthropic Claude API key for AI consultation
- `PORT` (optional): Server port, defaults to 8080

## Technical Stack

- **Backend**: FastAPI with Python 3.8+
- **AI Model**: Anthropic Claude 3.5 Sonnet
- **Frontend**: HTML with Jinja2 templates
- **Containerization**: Docker support
- **API Documentation**: Automatic OpenAPI/Swagger docs

## Traditional Chinese Concepts

This application integrates authentic fengshui principles including:

- **八卦 (Bagua)**: Eight trigrams for directional analysis
- **五行相生相剋**: Element generation and control cycles
- **季節能量**: Seasonal energy harmonization
- **方位學**: Directional feng shui guidance
- **氣場平衡**: Energy field balancing

## License

MIT License