# 📈 Stock Analysis Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org/)
[![Google Colab](https://img.shields.io/badge/Colab-Notebook-orange?logo=google-colab)](https://colab.research.google.com/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.0%20Flash-purple?logo=google)](https://ai.google.dev/)
[![Yahoo Finance](https://img.shields.io/badge/Yahoo-Finance-blueviolet)](https://finance.yahoo.com/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=google-colab)](https://colab.research.google.com/drive/1Wji69Sq-IqhtMEJTlxIkQ39ZZ5JAXR6w)

Multi-agent investment analysis system that automates stock screening, fundamental analysis, and investment report generation for Malaysian stocks. Designed for retail investors focused on long-term dividend investing with AI-powered research and scoring.

## 🚀 Live Demo

**[🌟 View Live Demo on Google Colab](https://colab.research.google.com/drive/1Wji69Sq-IqhtMEJTlxIkQ39ZZ5JAXR6w)**

## ✨ Features

- **🔍 Automated Stock Screening:** Filter stocks by PE ratio (4-15), ROE (≥5%), dividend yield (≥1%), price, and market cap
- **🤖 Multi-Agent Architecture:** 5 specialized AI agents working together for comprehensive analysis
- **📊 Investment Yardstick Scoring:** 7-category evaluation system (0-100 points) with buy/hold/avoid recommendations
- **💼 Fundamental Analysis:** Automated profitability, financial health, and valuation assessment
- **🏰 Business Moat Research:** AI-powered competitive advantage analysis using web search
- **💰 Dividend Sustainability:** Cash flow and dividend quality evaluation
- **📄 Professional Reports:** Investment reports in markdown format with visualizations
- **🔎 Stock Discovery:** Batch screening of 50+ stocks to find hidden gems
- **📈 Real-Time Data:** Yahoo Finance integration for live Malaysian stock market data

## 🛠️ Tech Stack

**AI & Processing:**
- **Google Gemini 2.0 Flash** - AI-powered analysis and investment scoring
- **Yahoo Finance API (yfinance)** - Real-time financial data for Malaysian stocks
- **Tavily API** - Web search for qualitative business moat research
- **Python 3.8+** - Core analytics and data processing

**Data Analysis:**
- **Pandas** - Financial data manipulation and analysis
- **Matplotlib & Seaborn** - Investment yardstick visualizations
- **JSON Processing** - Structured scoring and report generation

**Deployment:**
- **Google Colab** - Interactive notebook environment
- **Jupyter Notebook** - Local development and execution

## 🚀 Quick Start

### Prerequisites
- **Google Account** for Google Colab access
- **Gemini API Key** from Google AI Studio
- **Tavily API Key** for web search capabilities

### Option 1: Google Colab (Recommended)
```python
# Open the notebook directly in Google Colab
# Click: https://colab.research.google.com/drive/1Wji69Sq-IqhtMEJTlxIkQ39ZZ5JAXR6w

# Add your API keys to Colab Secrets:
# 1. Click the key icon (🔑) in the left sidebar
# 2. Add: GOOGLE_API_KEY and TAVILY_API_KEY
# 3. Run all cells
```

### Option 2: Local Jupyter Notebook
```bash
# Clone the repository
git clone https://github.com/lyven81/ai-project.git
cd ai-project/projects/stock-analysis-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install google-generativeai yfinance pandas matplotlib seaborn tavily-python

# Set up API keys
export GOOGLE_API_KEY="your_gemini_api_key"
export TAVILY_API_KEY="your_tavily_api_key"

# Run Jupyter notebook
jupyter notebook stock_analysis_agent.ipynb
```

## 📖 Usage

### Basic Stock Analysis

```python
# Analyze a single Malaysian stock
results = run_stock_analysis_pipeline('1818.KL')  # Bursa Malaysia

# View generated report and chart
print(f"Report: {results['report_path']}")
print(f"Chart: {results['chart_path']}")
```

### Stock Discovery (Batch Screening)

```python
# Discover stocks matching your investment criteria
discovery_results = discover_stocks(
    criteria={
        'max_price': 1.00,              # Price ≤ RM 1.00
        'min_pe': 4,                    # PE Ratio ≥ 4
        'max_pe': 15,                   # PE Ratio ≤ 15
        'min_roe': 5,                   # ROE ≥ 5%
        'min_eps': 0.01,                # EPS ≥ 0.01
        'min_dividend_yield': 1,        # Dividend Yield ≥ 1%
        'min_market_cap': 50_000_000,   # Market Cap ≥ RM 50M
        'min_volume': 50_000            # Volume ≥ 50,000 shares/day
    },
    max_stocks_to_scan=50,
    analyze_top_n=3  # Fully analyze top 3 passing stocks
)
```

## 🤖 Multi-Agent Architecture

### Agent 1: Stock Screener Agent 🔍
- Validates stocks against investment criteria
- Checks price, PE, ROE, EPS, dividend yield, market cap, volume
- Returns pass/fail status with detailed breakdown

### Agent 2: Fundamental Analyst Agent 📈
- **Fundamentals & Profitability (20 points):** ROE, EPS, profit margins
- **Financial Health & Solvency (15 points):** Debt ratios, current ratio, book value
- **Valuation (20 points):** PE ratio, price-to-book, price-to-sales

### Agent 3: Business Moat Analyst Agent 🏰
- Researches competitive advantages via web search
- Evaluates brand strength, network effects, cost advantages
- **Moat Score: 0-15 points**

### Agent 4: Dividend & Cash Flow Analyst Agent 💰
- Analyzes dividend sustainability and payout ratio
- Evaluates dividend history and growth trends
- **Dividend Score: 0-15 points**

### Agent 5: Investment Report Agent 📋
- Compiles all analysis into comprehensive markdown report
- Generates investment yardstick visualization
- Provides buy/hold/avoid recommendations

## 📊 Investment Yardstick (7 Categories)

| Category | Weight | Total Points |
|----------|--------|--------------|
| **Fundamentals & Profitability** | 20% | 20 |
| **Financial Health & Solvency** | 15% | 15 |
| **Valuation** | 20% | 20 |
| **Business Moat** | 15% | 15 |
| **Cash Flow & Dividends** | 15% | 15 |
| **Management & Outlook** | 10% | 10 |
| **Liquidity** | 5% | 5 |
| **TOTAL** | **100%** | **100** |

### Recommendation Scale

- **80-100 points:** Strong Buy 🟢
- **60-79 points:** Buy 🟡
- **40-59 points:** Hold ⚪
- **0-39 points:** Avoid 🔴

## 📝 Disclaimer

**IMPORTANT:** This tool is for educational and research purposes only. It is NOT financial advice. Always conduct your own due diligence and consult with licensed financial advisors.

## 📧 Contact

- **Portfolio:** [View More Projects](../../README.md)
- **Issues:** [Report Bugs](https://github.com/lyven81/ai-project/issues)

---

⭐ **If you found this project helpful, please give it a star!** ⭐

*AI-powered investment analysis for smarter stock decisions* 📈🤖
