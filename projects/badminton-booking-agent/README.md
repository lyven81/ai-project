# 🏸 Badminton Court Booking Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-purple?logo=google)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com/)

AI-powered agentic workflow for intelligent badminton court booking management using code-as-action pattern with Gemini 2.5 Flash.

## ✨ Features

- 🤖 Agentic AI Workflow - LLM generates executable Python code
- ⏰ 24/7 Operations - Round-the-clock booking
- 💰 Dynamic Pricing - 4 tiers (day/night × weekday/weekend)
- 🏸 12 Courts - Real-time availability
- 🔍 Conflict Detection - No double-booking
- 🌏 Malaysian Context - IC numbers, RM currency

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Add your GOOGLE_API_KEY

# Run API server
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

## 📖 API Endpoints

POST /api/chat - Chat with booking agent
GET /api/courts - List courts
GET /api/bookings - List bookings  
GET /api/revenue - Revenue statistics

## 💰 Pricing

| Time | Weekday | Weekend |
|------|---------|---------|
| Day (6am-6pm) | RM80 | RM90 |
| Night (6pm-6am) | RM100 | RM120 |

## 📁 Project Structure

- main.py - FastAPI application
- requirements.txt - Dependencies
- Dockerfile - Container config
- .env.example - Environment template

## 🎓 Learning Outcomes

- Agentic AI patterns (M5 code-as-action)
- LLM integration (Gemini API)
- REST API design (FastAPI)
- Safe code execution
- Time-based pricing logic

---

*Intelligent booking automation powered by agentic AI* 🏸🤖
