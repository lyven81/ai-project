# 🤖 Lee Yih Ven - AI Project Portfolio

[![Portfolio Website](https://img.shields.io/badge/Portfolio-Live-green?logo=vercel)](https://lyven81.github.io/ai-project/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/lyven81/ai-project)
[![Projects](https://img.shields.io/badge/Projects-43-blue)](#-featured-projects)
[![AI Powered](https://img.shields.io/badge/AI-Powered-orange?logo=tensorflow)](https://github.com/lyven81/ai-project)

**Innovative AI Solutions for Modern Challenges** - A curated collection of production-ready AI applications showcasing expertise in computer vision, natural language processing, document processing, and creative AI technologies.

<div align="center">
<img width="1200" height="400" alt="AI Portfolio Banner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

## 🌟 Portfolio Overview

This repository contains **43 production-deployed AI applications** demonstrating proficiency across multiple AI domains. Each project includes comprehensive documentation, live demos, and complete source code with deployment configurations.

**🎯 Portfolio Highlights:**
- **15+ AI Technologies** integrated across projects
- **Production Deployments** on Google Cloud Platform
- **Full-Stack Development** with modern frameworks
- **Professional Documentation** with setup guides and technical details
- **Real-World Applications** solving practical problems with AI

## AI Architecture Classification

Each project is classified by its AI architecture pattern, based on how the system processes queries, uses tools, and makes decisions.

### Multi-Agent Orchestration (1 project)
*Multiple specialized agents chained in sequence, each with its own tools and instructions.*

| Project | Why Multi-Agent |
|---|---|
| [Stock Manager](./projects/stock-manager/) | 3-agent ADK pipeline: Sales Analyst → Inventory Checker → Restock Decider → Google Sheets |

### Agentic AI (7 projects)
*Orchestrator with planning, tools, memory, and feedback loops. Autonomous decision-making.*

| Project | Why Agentic |
|---|---|
| [Business Intelligence Agent](./projects/business-intelligence-agent/) | NL query → plans analysis → writes code → executes → returns results |
| [Customer Segmentation Agent](./projects/customer-segmentation-agent/) | Autonomously profiles customers → segments → generates campaigns |
| [Data Consulting Business Analyst](./projects/data-consulting-business-analyst/) | 4-agent architecture: research → competitor intel → opportunity → strategy |
| [Sales Dashboard Agent](./projects/sales-dashboard-agent/) | NL query → plans viz → builds charts → iterates |
| [Stock Analysis Agent](./projects/stock-analysis-agent/) | 5-agent architecture: screening → fundamentals → moat → dividends → reporting |
| [Time Series Analysis Agent](./projects/time-series-analysis-agent/) | Upload data → plans analysis → executes → visualizes |
| [Public Sentiment Collection Agent](./projects/public-sentiment-collection-agent/) | 5-agent architecture: listening → sentiment → visualization → export → packaging |

### RAG — Retrieval-Augmented Generation (2 projects)
*Query → retrieve from knowledge base or external data → augment → LLM → output.*

| Project | Why RAG |
|---|---|
| [Claude PDF Summarizer](./projects/claude-pdf-summarizer/) | Upload doc → retrieve content → summarize |
| [Long View](./projects/long-view/) | 27 OSINT sources → delta detection → LLM synthesis → briefing |

### RPA — Robotic Process Automation (16 projects)
*Uses tools (APIs, image processing) but follows a fixed pipeline. No autonomous planning.*

| Project | Why RPA |
|---|---|
| [AI Avatar Hairstyle Generator](./projects/ai-avatar-hairstyle-generator/) | Upload → face extraction → 9 hairstyles → output |
| [AI Background Changer](./projects/ai-background-changer/) | Upload → subject preservation → background replace → output |
| [AI Coloring Book for Kids](./projects/ai-coloring-book-for-kids/) | Theme → generate page → interactive coloring |
| [AI Expression Generator](./projects/ai-expression-generator/) | Upload → generate 9 expressions → output |
| [AI Group Photo Generator](./projects/ai-group-photo-generator/) | Upload multiple → blend → output |
| [AI Photo Editor](./projects/ai-photo-editor/) | Upload → apply AI edits → output |
| [AI Profile Picture Stylist](./projects/ai-profile-picture-stylist/) | Upload → 4 professional styles → output |
| [Coloring Book Generator](./projects/coloring-book-generator/) | Prompt → generate pages → PDF output |
| [Image Recipe Generator](./projects/image-recipe-generator/) | Upload food photo → extract recipe → output |
| [PDF-to-Audio Reader](./projects/pdf-to-audio-reader/) | Upload PDF → TTS → audio output |
| [Polaroid Moments Generator](./projects/polaroid-moments-generator/) | Upload → vintage Polaroid style → output |
| [Polaroid Moments Generator 3](./projects/polaroid-moments-generator-3/) | Upload 3 photos → group composition → output |
| [Pose Perfect AI](./projects/pose-perfect-ai/) | Upload → pose detection → feedback → output |
| [Unusual Coloring Book](./projects/unusual-coloring-book/) | Story path → illustrate → color → export |
| [Virtual Try-On Studio](./projects/virtual-try-on-studio/) | Upload → overlay clothing → output |
| [Expense Tracker AI](./projects/expense-tracker-ai/) | Receipt → OCR → categorize → analytics |

### LLM Chatbots (14 projects)
*Query → system prompt → LLM → output. No tools, no memory, no planning.*

| Project | Why LLM Chatbot |
|---|---|
| [Fengshui Chatbot](./projects/fengshui-chatbot/) | Prompt-driven feng shui consultation |
| [Horoscope Chatbot](./projects/horoscope-chatbot/) | Zodiac Q&A, no tools or memory |
| [Master Wong](./projects/master-wong/) | I Ching readings, prompt-based |
| [Skyread](./projects/skyread/) | Daily horoscope generation |
| [Tarot Guru](./projects/tarot-guru/) | Card interpretation, prompt-driven |
| [Wiseman](./projects/wiseman/) | Chinese philosophy Q&A |
| [Kopitiam Digital Waiter](./projects/kopitiam-digital-waiter/) | Menu-based ordering, prompt-driven |
| [Football Assistant Coach](./projects/football-assistant-coach/) | Strategy Q&A, no external tools |
| [Nine Year Plan](./projects/nine-year-plan/) | Reference Q&A, prompt-based |
| [Sarawak Laksa](./projects/sarawak-laksa/) | Curated knowledge, prompt-based |
| [Banana Lab](./projects/banana-lab/) | Prompt pack generation |
| [MyPropLex](./projects/myproplex/) | Legal Q&A, prompt-driven |
| [Chinese Calendar](./projects/chinese-calender/) | Calendar lookup, prompt-based |
| [TrendMate](./projects/trendmate/) | Fashion trend Q&A |

### Hybrid Tools (3 projects)
*Uses LLM + external tools but not fully autonomous — some decision logic without full orchestration.*

| Project | Why Hybrid |
|---|---|
| [Badminton Booking Agent](./projects/badminton-booking-agent/) | Code-as-action pattern with LLM but follows booking flow |
| [Hire Gardener](./projects/hire-gardener/) | WhatsApp + vendor matching, semi-structured |
| [Social Media Marketer](./projects/social-media-marketer/) | Multi-agent simulation but fixed evaluation loop |

### Interactive Learning Tools (2 projects)
*Educational content generation with structured pedagogical output.*

| Project | Why Learning Tool |
|---|---|
| [Science Learning Materials Builder](./projects/science-learning-materials-builder/) | 4-agent lesson plan generator with curriculum alignment |
| [Thematic Outline Puzzles](./projects/thematic-outline-puzzles/) | Structured puzzle content generation |

### Architecture Summary

| Category | Count | % |
|---|---|---|
| LLM Chatbots | 14 | 32% |
| RPA (fixed pipelines) | 16 | 36% |
| RAG | 2 | 5% |
| Agentic AI | 7 | 16% |
| Hybrid Tools | 3 | 7% |
| Interactive Learning | 2 | 5% |

## 🚀 Live Portfolio Website

**[🌟 View Interactive Portfolio](https://lyven81.github.io/ai-project/)** - Experience all projects through the live demo website with organized categories and direct links to applications.

## 🏆 Featured Projects

### 📸 Computer Vision & Image Processing

#### [Pose Perfect AI](./projects/pose-perfect-ai/)
**Advanced computer vision for pose analysis and movement optimization**
- **Live Demo:** [pose-perfect-ai-169218045868.us-west1.run.app](https://pose-perfect-ai-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Computer Vision APIs, AI Pose Detection
- **AI Capabilities:** Real-time pose detection, form analysis, movement correction feedback

#### [Virtual Try-On Studio](./projects/virtual-try-on-studio/)
**AR-powered virtual clothing experience with AI-driven fitting**
- **Live Demo:** [virtual-try-on-studio-169218045868.us-west1.run.app](https://virtual-try-on-studio-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, AR/3D Processing, Computer Vision
- **AI Capabilities:** Virtual garment fitting, body measurement analysis, size recommendations

#### [AI Photo Editor](./projects/ai-photo-editor/)
**Professional-grade AI-powered photo editing with intelligent enhancement**
- **Live Demo:** [gemini-image-editor-169218045868.us-west1.run.app](https://gemini-image-editor-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Vite, Google Gemini AI
- **AI Capabilities:** Intelligent photo optimization, real-time filters, advanced image processing

#### [AI Group Photo Generator](./projects/ai-group-photo-generator/)
**Create stunning group compositions with advanced AI technology**
- **Live Demo:** [ai-group-photo-generator-169218045868.us-west1.run.app](https://ai-group-photo-generator-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, AI Image Generation, Computer Vision
- **AI Capabilities:** Group composition optimization, facial recognition, professional photo generation

### 📄 Document Processing & Analysis

#### [Claude PDF Summarizer](./projects/claude-pdf-summarizer/)
**Intelligent document processing with multi-language AI summarization**
- **Live Demo:** [summarizer-218391175125.asia-southeast1.run.app](https://summarizer-218391175125.asia-southeast1.run.app/)
- **Tech Stack:** Python, Streamlit, Claude 3 Haiku API, PDF Processing
- **AI Capabilities:** Multi-language summarization, executive/simple/kids formats, key insights extraction

#### [Expense Tracker AI](./projects/expense-tracker-ai/)
**Intelligent expense tracking with AI-powered receipt processing using Google Gemini**
- **Live Demo:** [expense-tracker-ai-169218045868.us-west1.run.app](https://expense-tracker-ai-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini AI, Recharts, Local Storage
- **AI Capabilities:** Receipt OCR processing, automatic data extraction, smart categorization, expense analytics

#### [PDF-to-Audio Reader](./projects/pdf-to-audio-reader/)
**Convert PDF documents into natural-sounding audio with AI-powered structuring**
- **Live Demo:** [pdf-to-audio-reader-169218045868.us-west1.run.app](https://pdf-to-audio-reader-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini AI, Web Speech API, PDF.js
- **AI Capabilities:** Document structure analysis, text-to-speech conversion, synchronized highlighting, chapter navigation

### 📊 Business Intelligence & Analytics Agents

#### [Good Company](./projects/good-company/)
**Stock research assistant that reads quarter report PDFs and runs a 7-step analysis to determine if a company is a good business and worth investing in**
- **Live Demo:** [Demo (Dialog Group)](./projects/good-company/demo.html)
- **Tech Stack:** Python, FastAPI, Gemini 2.5 Flash, PyMuPDF, Vanilla JS, marked.js
- **AI Capabilities:** 7-step phased analysis (company overview, forensic check, verdict, valuation, bull/bear debate, personal risk check, final scorecard), local PDF reading, 7 visualization types (metric cards, scorecards, verdict badges, range bars, scenario cards), one-click report copy, plain-language output with Goldman Sachs analytical depth

#### [Time Series Analysis Agent](./projects/time-series-analysis-agent/)
**AI-powered data analytics through natural language queries using Google Gemini**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1ZTfYPQZXObgxqk3hawGu9Sm33EjJX2xA)
- **Tech Stack:** Python, Gemini 2.0 Flash, Pandas, NumPy, Matplotlib, Seaborn
- **AI Capabilities:** Natural language to code generation, automated time series analysis, revenue trends, customer segmentation, profit margin analysis, correlation analysis, self-correcting with error handling

#### [Stock Analysis Agent](./projects/stock-analysis-agent/)
**Multi-agent investment research system with automated stock screening and fundamental analysis**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1Wji69Sq-IqhtMEJTlxIkQ39ZZ5JAXR6w)
- **Tech Stack:** Python, Gemini 2.0 Flash, Yahoo Finance API, Tavily API, Matplotlib
- **AI Capabilities:** 5-agent architecture (screening, fundamentals, business moat, dividends, reporting), investment yardstick scoring (0-100 points), web-powered competitive analysis, automated report generation with visualizations, Malaysian stock market analysis

#### [Sales Dashboard Agent](./projects/sales-dashboard-agent/)
**Natural language to code analytics with automated visualizations using code-as-plan pattern**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1ssz7RkCySo4fhzkLdCs5c7gCgkP7ypv7)
- **Tech Stack:** Python, Gemini 2.0 Flash, TinyDB, Pandas, Matplotlib, Seaborn
- **AI Capabilities:** Business question interpretation, Python code generation, safe execution sandbox, automated chart creation (bar/line/scatter), revenue/profit/customer analytics, read-only database security

#### [Science Learning Materials Builder](./projects/science-learning-materials-builder/)
**4-agent educational content generator for age-appropriate science lessons aligned with NGSS standards**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1p390KHKMQ9xcaDQ7eQTQJjdlX1JTxpmn)
- **Tech Stack:** Python, Gemini 2.0 Flash, Tavily API, WeasyPrint, Markdown Processing
- **AI Capabilities:** Curriculum research (web search + NGSS validation), visual illustration prompts, 3rd-grade reading level content writing, quiz generation (5 MC + 2 SA), hands-on activities, markdown + PDF export

#### [Public Sentiment Collection Agent](./projects/public-sentiment-collection-agent/)
**AI-powered geographic sentiment analysis with credibility tracking and source diversity assessment**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1On9i4SrYBVQqG-Fex5up9o3Eo1Y6mWls)
- **Tech Stack:** Python, Gemini 2.0 Flash, Tavily API, Pandas, Matplotlib, Seaborn
- **AI Capabilities:** 5-agent architecture (geographic listening, comparative sentiment analysis, visualization, data export, packaging), credibility scoring (0-100), source diversity tracking with bias detection, regional sentiment comparison, automatic quality warnings, 10 files per analysis (1 report, 4 charts, 5 CSV exports)

#### [Data Consulting Business Analysis Agent](./projects/data-consulting-business-analyst/)
**Automated market intelligence system for data analytics consulting firms - 100x faster than manual research**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1BZ1m_XsI5q7CHvdopcCK53Wlw0sCt1-j)
- **Tech Stack:** Python, Gemini 2.0 Flash, Tavily API, Matplotlib, Seaborn, NetworkX
- **AI Capabilities:** 4-agent architecture (industry research, competitor intelligence, opportunity analysis, strategic reporting), web-powered trend discovery, competitive capability matrix mapping, white-space opportunity detection, 2x2 strategic opportunity maps, executive-ready markdown reports with embedded visualizations

#### [Customer Segmentation Agent](./projects/customer-segmentation-agent/)
**AI-powered customer segmentation and targeted marketing campaign creation using RFM analysis**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/1UfEqslRGbYY4qOcv2SCDrj1e0dC5jqJl)
- **Tech Stack:** Python, Gemini 2.0 Flash, TinyDB, Pandas, Matplotlib, Seaborn, NumPy
- **AI Capabilities:** Natural language to code generation, RFM analysis (Recency, Frequency, Monetary), 5-segment customer classification (VIP, Regular, At-Risk, New, Churned), automated campaign targeting, customer profiling database, intelligent filter generation, self-correcting code execution

#### [Football Assistant Coach](./projects/football-assistant-coach/)
**AI-powered player selection system that evaluates 22 players across 4 training sessions and recommends the optimal Starting XI**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/football-assistant-coach/demo.html)
- **Tech Stack:** Python, Claude Haiku, Streamlit, Plotly, Pandas, Anthropic SDK
- **AI Capabilities:** 22 position-specific AI coach personas, team chemistry scoring (max 50 pts) weighted above individual performance (max 35 pts), formation-aware selection engine, hybrid formation advisor, rolling form calculation (60/40 two-week average), transfer risk detection

#### [Social Media Marketer](./projects/social-media-marketer/)
**Multi-agent simulation that reveals which marketing channel delivers the best ROI — and which one to cut**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/social-media-marketer/demo.html)
- **Tech Stack:** Python, Claude Haiku, Streamlit, Plotly, Pandas, Anthropic SDK
- **AI Capabilities:** 5 competing AI agents with distinct personas, structured JSON decision-making, economic scoring engine, CMO-level recommendations, real-time simulation progress, downloadable markdown reports

#### [Business Intelligence Agent](./projects/business-intelligence-agent/)
**General-purpose data analytics agent that answers business questions from any CSV dataset using natural language**
- **Live Demo:** [Google Colab](https://colab.research.google.com/drive/10wkxsg7Crcdz9oa3rFKlJ6Jtez1CB3xf)
- **Tech Stack:** Python, Gemini 2.0 Flash, Pandas, NumPy, Matplotlib, Seaborn
- **AI Capabilities:** Automatic schema detection and analysis, natural language to Pandas/NumPy code generation, safe sandboxed execution environment, automatic visualization generation, multi-pattern support (filtering, aggregation, grouping), error handling with status tracking, exploratory data analysis

#### [Kopitiam Digital Waiter](./projects/kopitiam-digital-waiter/)
**Real-time sales tracker and digital logbook for Malaysian Kopitiam owners with AI-powered business tips**
- **Live Demo:** [kopitiam-digital-waiter-169218045868.us-west1.run.app](https://kopitiam-digital-waiter-169218045868.us-west1.run.app/)
- **Tech Stack:** React 19, TypeScript, Express.js, SQLite, Vite, Tailwind CSS, Recharts, Gemini AI
- **AI Capabilities:** AI-powered contextual quick tips, milestone sales alerts, busy hour analytics, daily revenue trend visualization, real-time item performance ranking

#### [MyPropLex](./projects/myproplex/)
**AI-powered Malaysian property law research assistant for lawyers and conveyancers**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/myproplex/demo.html)
- **Tech Stack:** Python, Claude Sonnet 4.6, Tavily Search API, Streamlit
- **AI Capabilities:** ReAct agent loop with web search, Malaysian property law specialist (NLC, HDA, STA, RPGT, RERA), 3-sentence cited answers, 10 preset questions, conversation memory

#### [TrendMate](./projects/trendmate/)
**AI market research assistant for Malaysian online fashion sellers on Shopee, Lazada, and TikTok Shop**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/trendmate/demo.html)
- **Tech Stack:** Python, Claude Sonnet 4.6, Tavily Search API, Streamlit
- **AI Capabilities:** ReAct agent loop with web search, Malaysian fashion market specialist, trend/pricing/supplier/seasonal research, 3-sentence actionable answers, 10 preset questions

### 🤖 Business Automation & Booking Systems

#### [Hire Gardener](./projects/hire-gardener/)
**AI agent that finds, negotiates with, and hires a grass cutting service entirely via WhatsApp**
- **Live Demo:** [Try Demo](https://lyven81.github.io/ai-project/projects/hire-gardener/demo.html)
- **Tech Stack:** Python, Streamlit, Ollama, Llama3, Meta WhatsApp Cloud API
- **AI Capabilities:** 6-stage vendor communication workflow, Llama3 vendor persona simulation, pluggable mock/live mode switch, natural Malaysian English/Malay conversation, AI job completion verification

#### [Banana Lab](./projects/banana-lab/)
**Automated AI prompt pack store — Claude writes, packages, and lists a new 50-prompt product every Monday**
- **Live Demo:** [View Store](https://lyven81.github.io/ai-project/projects/banana-lab/demo.html)
- **Tech Stack:** Python 3, Claude API (claude-sonnet-4-6), schedule library, Gmail SMTP, Static HTML/CSS, Gumroad
- **AI Capabilities:** Automated niche research (avoids duplicates), batched 50-prompt generation (2 API calls), structured JSON output, Markdown product files with ready-to-paste Gumroad listing copy, self-updating website

#### [Marketing Agency](./projects/marketing-agency/)
**Autonomous content marketing system that produces weekly blog posts, LinkedIn drafts, and lead follow-ups for solo consultancy firms**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/marketing-agency/demo.html)
- **Tech Stack:** Python, FastAPI, Jinja2, httpx, Claude Code Skills, Ollama
- **AI Capabilities:** 6-skill content pipeline chaining, brand voice enforcement, lead urgency scoring via Ollama, campaign phase-aware topic selection, dual-brand content (analytics + AI solutions), feedback loop connecting lead data to topic selection

#### [Badminton Court Booking Agent](./projects/badminton-booking-agent/)
**AI-powered agentic workflow for intelligent badminton court booking management using code-as-action pattern**
- **Live Demo:** [ai-profile-badminton-court-booking--662370080553.us-west1.run.app](https://ai-profile-badminton-court-booking--662370080553.us-west1.run.app/)
- **Tech Stack:** Python, FastAPI, Google Gemini 2.5 Flash, TinyDB, Pydantic, Docker
- **AI Capabilities:** M5 pattern (code-as-action) for agentic workflows, LLM generates executable Python code for booking operations, dynamic time-based pricing (4 tiers: daytime/nighttime × weekday/weekend), multi-hour bookings with per-hour pricing breakdown, automatic conflict detection and double-booking prevention, 24/7 operations with midnight-crossing bookings, revenue tracking and financial analytics, Malaysian localization (IC numbers, RM currency), natural language processing for flexible date/time parsing, safe code execution in controlled namespace

### 🤖 Conversational AI & Specialized Chatbots

#### [Mentor](./mentor.html)
**AI advisor for solo founders of service and expert businesses — grounded in proven frameworks, not generic chatbot fluff**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/mentor/demo.html)
- **Tech Stack:** Python Flask, Claude Haiku 4.5, Anthropic SDK, Vanilla JS, marked.js
- **AI Capabilities:** Unified-voice synthesis of multiple expert sources, keyword-retrieval grounding, two-layer context (always-on reality + retrieved frameworks), strict output contract (≤2 paragraphs, ≤3 sentences each), candid but encouraging tone, session memory for natural follow-ups, persistent chat log archive

#### [Tarot Guru](./projects/tarot-guru/)
**AI-powered personal tarot reading app that uses cards as a mirror for reflection and clarity**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/tarot-guru/demo.html)
- **Tech Stack:** Node.js, Express, Claude Opus API, Vanilla JS, Local JSON Storage
- **AI Capabilities:** Context-aware spread recommendation (1 / 3-card / Celtic Cross), narrative reading connected to user's specific question, follow-up chat with session memory, session archive as timestamped JSON files

#### [Wiseman · 智者](./projects/wiseman/)
**Daily cosmic reading in Mandarin Chinese combining Bazi, Western horoscope, planetary astrology, and Chinese zodiac**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/wiseman/demo.html)
- **Tech Stack:** Node.js, Express, Claude Opus API, Vanilla JS, Daily JSON Cache
- **AI Capabilities:** 5-panel dashboard (八字/星座/行星/生肖/综合解读), personalized to birth date and zodiac signs, one reading per day cached for instant reload, floating chat for follow-up questions in Mandarin

#### [Master Wong · 王师父](./projects/master-wong/)
**Personal I Ching oracle powered by Claude AI — readings in plain conversational Mandarin Chinese**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/master-wong/demo.html)
- **Tech Stack:** Node.js, Express, Claude Sonnet API, Vanilla JS, Three-Coin Casting Engine
- **AI Capabilities:** Traditional three-coin casting mechanic, AI-recommended reading type (单卦/变卦/对比卦), situation-specific interpretation in plain Mandarin, changing line analysis, follow-up chat with hexagram context

#### [Long View · Crucix](./projects/long-view/)
**OSINT intelligence aggregator with 27 data sources, 3D globe visualization, and multi-LLM briefings**
- **Live Demo:** [Launch Demo](https://lyven81.github.io/ai-project/projects/long-view/demo.html)
- **Tech Stack:** Node.js 22+, Express, Multi-LLM (Claude/OpenAI/Gemini/Codex), WebGL/Three.js, Telegram Bot, Discord Bot, Docker
- **AI Capabilities:** 27 OSINT source aggregation, delta engine for meaningful change detection, provider-agnostic LLM synthesis, 3D globe visualization, Telegram/Discord push alerts, configurable 15-minute sweep cycle

#### [Chinese Traditional Calendar with AI Consultant (中華傳統日曆)](./projects/chinese-calender/)
**Revolutionary conversational AI-powered traditional Chinese lunar calendar with personalized auspicious date consultation**
- **Live Demo:** [chinese-calender-169218045868.asia-southeast1.run.app](https://chinese-calender-169218045868.asia-southeast1.run.app/)
- **Tech Stack:** Python, FastAPI, Progressive Web App, Conversational AI, Traditional Chinese Calendar Algorithms
- **AI Capabilities:** Natural language calendar consultation, personalized auspicious date recommendations, cultural education, intent recognition, real-time chat interface

#### [Professional Astrology Consultant (專業星座顧問)](./projects/horoscope-chatbot/)
**AI-powered personalized horoscope readings and astrological insights**
- **Live Demo:** [horoscope-chatbot-218391175125.asia-southeast1.run.app](https://horoscope-chatbot-218391175125.asia-southeast1.run.app/)
- **Tech Stack:** Python, Streamlit, Claude API, Traditional Chinese NLP
- **AI Capabilities:** Personalized readings, cultural context understanding, astrological analysis

#### [Professional Feng Shui Consultant (專業風水顧問)](./projects/fengshui-chatbot/)
**Expert Feng Shui consultation with AI assistance and traditional wisdom**
- **Live Demo:** [fengshui-chatbot-218391175125.asia-southeast1.run.app](https://fengshui-chatbot-218391175125.asia-southeast1.run.app/)
- **Tech Stack:** Python, Streamlit, Claude API, Cultural Knowledge Processing
- **AI Capabilities:** Space optimization recommendations, traditional wisdom integration, personalized advice

#### [Skyread](./projects/skyread/)
**Daily horoscope app that explains the planetary movements behind every reading for grounded, credible insights**
- **Live Demo:** [ais-dev-m2gjhpuvdrj3c3mly7e6rr-168381537832.asia-east1.run.app](https://ais-dev-m2gjhpuvdrj3c3mly7e6rr-168381537832.asia-east1.run.app)
- **Tech Stack:** React, TypeScript, Vite, Gemini AI, Framer Motion, Tailwind CSS
- **AI Capabilities:** Schema-enforced structured horoscope generation, bilingual EN/ZH AI output, real planetary movement explanations (Sky Explainer), Sky Snapshot panel, smart daily caching with localStorage

### 🎨 Creative AI & Content Generation

#### [Unusual Coloring Book](./projects/unusual-coloring-book/)
**Step inside Cinderella — choose your own story path, watch the AI illustrate it, colour it in, export to PDF**
- **Source Code:** [unusual-coloring-book-source.html](https://lyven81.github.io/ai-project/unusual-coloring-book-source.html)
- **Tech Stack:** React 18 + TypeScript, Python FastAPI, Gemini 3 Flash, Gemini Nano Banana 2, HTML5 Canvas, jsPDF
- **AI Capabilities:** On-demand illustration generation per story path, image editing via text instruction, server-side image caching

#### [AI Recipe Generator](./projects/image-recipe-generator/)
**Transform food images into detailed recipes with computer vision and NLP**
- **Live Demo:** [image-recipe-generator-218391175125.us-central1.run.app](https://image-recipe-generator-218391175125.us-central1.run.app/)
- **Tech Stack:** Python, Computer Vision, NLP, Image Recognition APIs
- **AI Capabilities:** Food image analysis, ingredient recognition, step-by-step recipe generation

#### [Polaroid Moments Generator](./projects/polaroid-moments-generator/)
**Create nostalgic retro-style photos by blending personal images with AI**
- **Live Demo:** [polaroid-moments-generator-169218045868.us-west1.run.app](https://polaroid-moments-generator-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini AI, Advanced Image Processing
- **AI Capabilities:** Dual image blending, pose synthesis, vintage aesthetic generation, facial preservation

#### [AI Avatar Hairstyle Generator](./projects/ai-avatar-hairstyle-generator/)
**Transform single photos into 9 different hairstyle avatars with AI-powered virtual styling**
- **Live Demo:** [ai-avatar-hairstyle-generator-169218045868.us-west1.run.app](https://ai-avatar-hairstyle-generator-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini AI, Computer Vision, Image Generation
- **AI Capabilities:** Face extraction, hairstyle application, identity preservation, photorealistic avatar creation

#### [AI Expression Generator](./projects/ai-expression-generator/)
**Generate 9 different emotional expressions from a single photo using advanced AI technology**
- **Live Demo:** [ai-expression-generator-169218045868.us-west1.run.app](https://ai-expression-generator-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini 2.5 Flash, Multimodal AI, Image Processing
- **AI Capabilities:** Facial expression transformation, identity preservation, emotional range generation, photorealistic quality

#### [Polaroid Moments Generator 3](./projects/polaroid-moments-generator-3/)
**Create nostalgic three-person group photos with AI-powered storytelling and vintage aesthetics**
- **Live Demo:** [polaroid-moments-generator-3-person-169218045868.us-west1.run.app](https://polaroid-moments-generator-3-person-169218045868.us-west1.run.app/)
- **Tech Stack:** React, TypeScript, Gemini AI, Advanced Multi-Image Processing
- **AI Capabilities:** Three-person group composition, story-driven pose generation, social dynamics modeling, vintage polaroid aesthetics

#### [AI Profile Picture Stylist](./projects/ai-profile-picture-stylist/)
**Transform single photos into 4 professional profile picture styles using Google Gemini AI**
- **Live Demo:** [ai-profile-picture-stylist-662370080553.us-west1.run.app](https://ai-profile-picture-stylist-662370080553.us-west1.run.app/)
- **Tech Stack:** React 19, TypeScript, Vite, Google Gemini AI, Tailwind CSS
- **AI Capabilities:** Smart people detection, professional style generation, Classic B&W/Corporate/Lifestyle/Editorial styles, instant validation

#### [AI Background Changer](./projects/ai-background-changer/)
**Intelligent image background replacement using natural language prompts and Gemini AI**
- **Live Demo:** [ai-background-changer-169218045868.us-west1.run.app](https://ai-background-changer-169218045868.us-west1.run.app/)
- **Tech Stack:** React 19, TypeScript, Gemini 2.5 Flash, Multimodal AI, Canvas API
- **AI Capabilities:** Natural language background understanding, subject preservation, seamless background replacement, context-aware generation

#### [AI Coloring Book for Kids](./projects/ai-coloring-book-for-kids/)
**Interactive educational coloring experience powered by AI with child-centered design and motor skill development**
- **Live Demo:** [ai-coloring-book-for-kids-662370080553.us-west1.run.app](https://ai-coloring-book-for-kids-662370080553.us-west1.run.app/)
- **Tech Stack:** React 19.1+, TypeScript 5.8+, Gemini AI, Canvas API, Educational Technology
- **AI Capabilities:** Theme-based coloring page generation, child-safe content filtering, educational AI prompts, interactive learning experiences

#### [AI Storybook Generator](./projects/ai-storybook-generator/)
**Interactive storybook creation with AI-generated narratives and coloring book illustrations for educational engagement**
- **Live Demo:** [ai-storybook-color-create-662370080553.us-west1.run.app](https://ai-storybook-color-create-662370080553.us-west1.run.app/)
- **Tech Stack:** React 19.1+, TypeScript 5.8+, Gemini 2.5 Flash, Imagen 4.0, Canvas API, Interactive Design
- **AI Capabilities:** Multi-page story generation, narrative continuity, interactive coloring canvas, drag-and-drop text editing, flood-fill algorithms

#### [Coloring Book Generator](./projects/coloring-book-generator/)
**AI-powered coloring book generator that creates custom-themed, printable PDF coloring books with age-appropriate complexity**
- **Live Demo:** [coloring-book-generator-662370080553.us-west1.run.app](https://coloring-book-generator-662370080553.us-west1.run.app/)
- **Tech Stack:** React 19.1+, TypeScript 5.8+, Gemini 2.5 Flash, Imagen 4.0, PDF Generation, Tailwind CSS
- **AI Capabilities:** Two-stage AI pipeline, theme interpretation, sequential page creation, age-adaptive complexity, print optimization

#### [Sarawak Laksa](./projects/sarawak-laksa/)
**Interactive curated reference on Kuching's most iconic dish — ingredients, recipe, where to eat, and cultural context**
- **Live Demo:** [lyven81.github.io/ai-project/projects/sarawak-laksa/](https://lyven81.github.io/ai-project/projects/sarawak-laksa/)
- **Tech Stack:** HTML5, CSS3, Vanilla JS, IntersectionObserver, Google Fonts
- **Features:** 7-section reference site — origin, ingredients, 4-phase recipe, 5 regional variations, 6 Kuching stalls, food culture, notable people

#### [Nine Year Plan 2022–2031](./projects/nine-year-plan/)
**Interactive reference guide to the Bahá'í Nine Year Plan — overview, core activities, institutions, statistics, and key messages**
- **Live Demo:** [lyven81.github.io/ai-project/projects/nine-year-plan/](https://lyven81.github.io/ai-project/projects/nine-year-plan/)
- **Tech Stack:** HTML5, CSS3, Vanilla JS, requestAnimationFrame, IntersectionObserver, Google Fonts
- **Features:** 8-section reference site — plan overview, history, core activities, framework, institutions, social action, animated stat counters, key messages

## 🛠️ Technical Skills Demonstrated

### **AI & Machine Learning**
- **Computer Vision:** Pose detection, facial recognition, image processing, AR/3D rendering
- **Natural Language Processing:** Multi-language support, document summarization, conversational AI
- **Data Analytics & BI:** Natural language to code generation, time series analysis, automated insights
- **Image Generation:** AI-powered photo creation, style transfer, composition optimization
- **Creative AI:** Content generation, recipe creation, vintage photo synthesis

### **Frontend Development**
- **Modern React:** React 18, TypeScript 5.0, modern hooks and concurrent features
- **Build Tools:** Vite, advanced bundling, code splitting, performance optimization
- **UI/UX Design:** Responsive design, interactive components, accessibility standards
- **State Management:** Context API, custom hooks, complex application state

### **Backend & APIs**
- **Python Development:** FastAPI, Streamlit, async programming, data processing
- **AI API Integration:** Google Gemini, Claude 3, OpenAI, specialized computer vision APIs
- **Database Management:** Data persistence, caching, optimization strategies
- **API Design:** RESTful services, error handling, rate limiting, security

### **Cloud & Deployment**
- **Google Cloud Platform:** Cloud Run, Container Registry, Build automation
- **Containerization:** Docker, multi-stage builds, optimization for production
- **CI/CD Pipelines:** Automated testing, deployment, monitoring
- **Performance Optimization:** Caching strategies, CDN integration, load balancing

### **Development Tools & Practices**
- **Version Control:** Git workflows, branching strategies, collaborative development
- **Code Quality:** ESLint, Prettier, TypeScript strict mode, testing frameworks
- **Documentation:** Comprehensive README files, API documentation, deployment guides
- **Security:** Environment variable management, API key security, input validation

## 📁 Repository Structure

```
ai-project/
├── index.html                    # Interactive portfolio homepage
├── project-categories.html       # Organized project categories
├── contact.html                  # Contact information
├── projects/                     # Complete project source code
│   ├── pose-perfect-ai/         # Computer vision pose analysis
│   ├── virtual-try-on-studio/   # AR virtual clothing experience
│   ├── ai-photo-editor/         # AI-powered photo editing
│   ├── ai-group-photo-generator/ # Group photo composition AI
│   ├── claude-pdf-summarizer/   # Document processing & summarization
│   ├── expense-tracker-ai/      # AI-powered expense tracking
│   ├── pdf-to-audio-reader/     # PDF to audio conversion with AI
│   ├── time-series-analysis-agent/ # Natural language data analytics
│   ├── stock-analysis-agent/    # Multi-agent stock analysis
│   ├── sales-dashboard-agent/   # Natural language analytics
│   ├── science-learning-materials-builder/ # Educational content generator
│   ├── public-sentiment-collection-agent/ # Geographic sentiment analysis
│   ├── data-consulting-business-analyst/ # Market intelligence system
│   ├── customer-segmentation-agent/ # RFM analysis & targeted campaigns
│   ├── business-intelligence-agent/ # Natural language data analytics
│   ├── kopitiam-digital-waiter/ # Real-time Kopitiam sales tracker & analytics
│   ├── myproplex/               # Malaysian property law research assistant
│   ├── trendmate/               # Malaysian fashion market research assistant
│   ├── chinese-calender/        # Conversational AI traditional calendar
│   ├── horoscope-chatbot/       # Astrology consultation AI
│   ├── fengshui-chatbot/        # Feng Shui advisory AI
│   ├── skyread/                 # Daily horoscope with planetary insights
│   ├── image-recipe-generator/  # Food image to recipe AI
│   ├── polaroid-moments-generator/ # Vintage photo generation AI
│   ├── polaroid-moments-generator-3/ # Three-person group photo AI
│   ├── ai-avatar-hairstyle-generator/ # Virtual hairstyle avatar generation
│   ├── ai-expression-generator/ # Emotional expression transformation AI
│   ├── ai-profile-picture-stylist/ # Professional profile picture styling AI
│   ├── ai-background-changer/   # Natural language background replacement AI
│   ├── ai-coloring-book-for-kids/ # Educational AI coloring book
│   ├── ai-storybook-generator/  # Interactive storybook creation with AI narratives
│   └── coloring-book-generator/ # AI-powered PDF coloring book creation
└── README.md                    # This comprehensive overview
```

Each project directory contains:
- **Complete source code** with production-ready implementations
- **Comprehensive README** with setup instructions and technical details
- **Deployment configurations** for cloud platforms
- **Environment setup guides** and dependency management
- **Live demo links** and usage examples

## 🚀 Getting Started

### Quick Start for Any Project
```bash
# Clone the repository
git clone https://github.com/lyven81/ai-project.git
cd ai-project

# Navigate to specific project
cd projects/[project-name]

# Follow individual project README for setup
```

### General Requirements
- **Node.js 16+** for React-based projects
- **Python 3.8+** for Streamlit applications
- **API Keys** for AI services (Gemini, Claude, etc.)
- **Docker** for containerized deployment (optional)

## 🌐 Live Demos & Deployment

All projects are production-deployed and accessible via live demos:

| Project | Live Demo | Category |
|---------|-----------|----------|
| Pose Perfect AI | [Launch App](https://pose-perfect-ai-169218045868.us-west1.run.app/) | Computer Vision |
| Virtual Try-On Studio | [Launch App](https://virtual-try-on-studio-169218045868.us-west1.run.app/) | Computer Vision |
| AI Photo Editor | [Launch App](https://gemini-image-editor-169218045868.us-west1.run.app/) | Image Processing |
| AI Group Photo Generator | [Launch App](https://ai-group-photo-generator-169218045868.us-west1.run.app/) | Creative AI |
| Claude PDF Summarizer | [Launch App](https://summarizer-218391175125.asia-southeast1.run.app/) | Document Processing |
| Expense Tracker AI | [Launch App](https://expense-tracker-ai-169218045868.us-west1.run.app/) | Document Processing |
| PDF-to-Audio Reader | [Launch App](https://pdf-to-audio-reader-169218045868.us-west1.run.app/) | Document Processing |
| Time Series Analysis Agent | [Launch in Colab](https://colab.research.google.com/drive/1ZTfYPQZXObgxqk3hawGu9Sm33EjJX2xA) | Business Intelligence |
| Stock Analysis Agent | [Launch in Colab](https://colab.research.google.com/drive/1Wji69Sq-IqhtMEJTlxIkQ39ZZ5JAXR6w) | Business Intelligence |
| Sales Dashboard Agent | [Launch in Colab](https://colab.research.google.com/drive/1ssz7RkCySo4fhzkLdCs5c7gCgkP7ypv7) | Business Intelligence |
| Science Learning Materials Builder | [Launch in Colab](https://colab.research.google.com/drive/1p390KHKMQ9xcaDQ7eQTQJjdlX1JTxpmn) | Business Intelligence |
| Public Sentiment Collection Agent | [Launch in Colab](https://colab.research.google.com/drive/1On9i4SrYBVQqG-Fex5up9o3Eo1Y6mWls) | Business Intelligence |
| Data Consulting Business Analysis Agent | [Launch in Colab](https://colab.research.google.com/drive/1BZ1m_XsI5q7CHvdopcCK53Wlw0sCt1-j) | Business Intelligence |
| Customer Segmentation Agent | [Launch in Colab](https://colab.research.google.com/drive/1UfEqslRGbYY4qOcv2SCDrj1e0dC5jqJl) | Business Intelligence |
| Business Intelligence Agent | [Launch in Colab](https://colab.research.google.com/drive/10wkxsg7Crcdz9oa3rFKlJ6Jtez1CB3xf) | Business Intelligence |
| Kopitiam Digital Waiter | [Launch App](https://kopitiam-digital-waiter-169218045868.us-west1.run.app/) | Business Intelligence |
| MyPropLex | [Launch Demo](https://lyven81.github.io/ai-project/projects/myproplex/demo.html) | Business Intelligence |
| Social Media Marketer | [Launch Demo](https://lyven81.github.io/ai-project/projects/social-media-marketer/demo.html) | Business Intelligence |
| TrendMate | [Launch Demo](https://lyven81.github.io/ai-project/projects/trendmate/demo.html) | Business Intelligence |
| Hire Gardener | [Launch Demo](https://lyven81.github.io/ai-project/projects/hire-gardener/demo.html) | Business Automation |
| Chinese Traditional Calendar | [Launch App](https://chinese-calender-169218045868.asia-southeast1.run.app/) | Conversational AI |
| Astrology Consultant | [Launch App](https://horoscope-chatbot-218391175125.asia-southeast1.run.app/) | Conversational AI |
| Feng Shui Consultant | [Launch App](https://fengshui-chatbot-218391175125.asia-southeast1.run.app/) | Conversational AI |
| Skyread | [Launch App](https://ais-dev-m2gjhpuvdrj3c3mly7e6rr-168381537832.asia-east1.run.app) | Conversational AI |
| AI Recipe Generator | [Launch App](https://image-recipe-generator-218391175125.us-central1.run.app/) | Creative AI |
| Polaroid Moments Generator | [Launch App](https://polaroid-moments-generator-169218045868.us-west1.run.app/) | Creative AI |
| Polaroid Moments Generator 3 | [Launch App](https://polaroid-moments-generator-3-person-169218045868.us-west1.run.app/) | Creative AI |
| AI Avatar Hairstyle Generator | [Launch App](https://ai-avatar-hairstyle-generator-169218045868.us-west1.run.app/) | Creative AI |
| AI Expression Generator | [Launch App](https://ai-expression-generator-169218045868.us-west1.run.app/) | Creative AI |
| AI Profile Picture Stylist | [Launch App](https://ai-profile-picture-stylist-662370080553.us-west1.run.app/) | Creative AI |
| AI Background Changer | [Launch App](https://ai-background-changer-169218045868.us-west1.run.app/) | Creative AI |
| AI Coloring Book for Kids | [Launch App](https://ai-coloring-book-for-kids-662370080553.us-west1.run.app/) | Creative AI |
| AI Storybook Generator | [Launch App](https://ai-storybook-color-create-662370080553.us-west1.run.app/) | Creative AI |
| Coloring Book Generator | [Launch App](https://coloring-book-generator-662370080553.us-west1.run.app/) | Creative AI |
| Sarawak Laksa | [Launch Demo](https://lyven81.github.io/ai-project/projects/sarawak-laksa/) | Creative AI |
| Nine Year Plan 2022–2031 | [Launch Demo](https://lyven81.github.io/ai-project/projects/nine-year-plan/) | Creative AI |

## 💼 Professional Highlights

### **Production-Ready Applications**
- All projects deployed on Google Cloud Platform with professional-grade infrastructure
- Comprehensive error handling, logging, and monitoring
- Optimized for performance, scalability, and user experience
- Security best practices implemented throughout

### **Business Impact Demonstration**
- **Time Savings:** Document processing reduces manual review time by 80%+
- **User Engagement:** Interactive AI experiences with high retention rates
- **Innovation:** Cutting-edge AI applications solving real-world problems
- **Accessibility:** Multi-language support expanding global reach

### **Technical Excellence**
- **Code Quality:** TypeScript strict mode, comprehensive testing, clean architecture
- **Performance:** Optimized loading times, efficient AI processing, responsive design
- **Documentation:** Professional-level documentation exceeding industry standards
- **Deployment:** Automated CI/CD pipelines with zero-downtime deployments

## 📞 Contact & Collaboration

**Portfolio Website:** [ai-project](https://lyven81.github.io/ai-project/)  
**GitHub Repository:** [lyven81/ai-project](https://github.com/lyven81/ai-project)

This portfolio demonstrates expertise in building production-ready AI applications that combine cutting-edge technology with practical business solutions. Each project showcases different aspects of modern AI development, from computer vision and natural language processing to creative content generation.

---

⭐ **Interested in AI solutions for your business? Let's collaborate!** ⭐

*Transforming ideas into intelligent applications through the power of artificial intelligence* 🤖✨