# Stock Manager

Smart restocking system for a steam bun shop, built with Google ADK multi-agent architecture.

**Live Demo:** [Browser-side BYO-key Gemini demo](./demo.html) (the Cloud Run + AlloyDB backend was retired on 2026-05-07 after the Top 100 evaluation closed; static demo runs entirely in the browser using your own Gemini API key)

## Problem

A steam bun shop restocks by over-ordering slow-moving items and running out of fast sellers. Without data-driven insights, they waste money on excess stock and lose sales from stockouts.

## Solution

Stock Manager uses multiple AI agents to automate restocking. It analyzes sales trends, monitors stock levels, predicts potential stockouts, and generates a purchase order in Google Sheets — all from a single question.

## Architecture

```
User (Browser)
      │ HTTP
      ▼
Cloud Run (FastAPI)
      │
      ▼
Google ADK (SequentialAgent)
      │
      ├── Sales Analyst Agent ──→ AlloyDB (sales data)
      ├── Inventory Checker Agent ──→ AlloyDB (stock levels)
      └── Restock Decider Agent ──→ Google Sheets (MCP)
```

## Tech Stack

| Technology | Role |
|-----------|------|
| Google ADK | Multi-agent orchestration (SequentialAgent) |
| Gemini 2.5 Flash | AI model for each agent |
| AlloyDB | Database (products, sales, inventory, suppliers) |
| Google Sheets (MCP) | Purchase order output |
| Cloud Run | Deployment (asia-southeast1) |
| FastAPI | Backend API |

## Features

1. **Sales Trend Analysis** — Identifies fast/slow movers and rising demand from AlloyDB
2. **Stock Level Monitoring** — Checks inventory against reorder points
3. **Predictive Restocking** — Recommends early restocking for trending items before stockouts
4. **Automated Purchase Order** — Creates purchase orders grouped by supplier in Google Sheets
5. **Natural Language Interface** — Ask one question, get a complete answer

## Multi-Agent Workflow

1. Shop owner asks: "What should I restock this week?"
2. **Sales Analyst** queries AlloyDB for sales trends and rising demand
3. **Inventory Checker** compares current stock against reorder points
4. **Restock Decider** combines both inputs — restocks low stock items AND items trending toward stockout
5. **Order Generator** creates a purchase order and pushes it to Google Sheets

## Dataset

Synthetic dataset for a steam bun shop with 18 products (buns, dim sum, pastries):
- 4 suppliers with lead times
- 9,852 sales transactions over 6 months
- Current inventory with mix of critical, low, and healthy stock levels

## Project Structure

```
├── main.py              # FastAPI app + API endpoints
├── agents.py            # ADK agent definitions (SequentialAgent + 3 sub-agents)
├── tools.py             # Tool functions (AlloyDB queries + Google Sheets)
├── schema.sql           # Database schema (4 tables)
├── db_setup.py          # Load CSV data into AlloyDB
├── static/
│   └── index.html       # Chat UI with inventory panel
├── dataset/
│   ├── suppliers.csv
│   ├── products.csv
│   ├── sales.csv
│   └── inventory.csv
├── Dockerfile
└── requirements.txt
```

## Setup

### Environment Variables

```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=asia-southeast1
GOOGLE_GENAI_USE_VERTEXAI=true
DB_HOST=your-alloydb-ip
DB_USER=postgres
DB_PASS=your-password
DB_NAME=stockmanager
GOOGLE_SHEETS_ID=your-spreadsheet-id
```

### Deploy to Cloud Run

```bash
gcloud run deploy stock-manager \
  --source . \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --vpc-connector your-vpc-connector \
  --set-env-vars "..." \
  --memory 1Gi \
  --timeout 300
```

## Google Gen AI Academy APAC 2026 — Cohort 2 Hackathon
