# Kereta Sewa Jalan-jalan — Car Rental Booking Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-purple?logo=google)](https://ai.google.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com/)

AI-powered agentic workflow for car rental bookings across Klang Valley using the code-as-action pattern with Gemini 2.5 Flash.

## Features

- 56 vehicles across 5 tiers (Economy, Compact, SUV, MPV, Premium)
- 4 pickup locations (KLIA, KL Sentral, Subang Airport, TBS) — free
- RM 100 booking deposit, daily/weekly pricing, optional RM 50 hotel delivery
- Status tracking: available / rented / booked / maintenance
- Natural language chat powered by Gemini code-as-action
- Malaysian context: RM currency, local plate numbers, Malaysian driving licenses

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add GOOGLE_API_KEY
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

## API Endpoints

- POST /api/chat - Chat with rental agent
- GET /api/vehicles - List vehicles
- GET /api/bookings - List bookings
- GET /api/revenue - Revenue statistics

## Fleet & Pricing

| Tier | Models | Daily | Weekly |
|---|---|---|---|
| Economy | Perodua Axia, Myvi | RM 120 | RM 700 |
| Compact | Honda City, Toyota Vios | RM 160 | RM 950 |
| SUV | Proton X50, Honda HR-V | RM 250 | — |
| MPV | Perodua Alza, Toyota Avanza | RM 220 | — |
| Premium | Toyota Camry, Honda Accord | RM 350 | — |

Booking deposit RM 100 (deducted from final bill). Hotel delivery add-on RM 50.
Min rental 1 day, max 7 days. Operating hours 08:00–20:00 daily.

## Requirements to Book

- Customer name
- Phone number
- Malaysian driving license number

## Project Structure

- main.py - FastAPI application
- demo.html - Self-contained client-side demo
- requirements.txt - Dependencies
- Dockerfile - Container config

---

*Intelligent car rental automation powered by agentic AI*
