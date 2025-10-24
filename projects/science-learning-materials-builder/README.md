# 🔬 Science Learning Materials Builder

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://python.org/)
[![Google Colab](https://img.shields.io/badge/Colab-Notebook-orange?logo=google-colab)](https://colab.research.google.com/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.0%20Flash-purple?logo=google)](https://ai.google.dev/)
[![Tavily API](https://img.shields.io/badge/Tavily-Search-green)](https://tavily.com/)
[![Live Demo](https://img.shields.io/badge/Live-Demo-green?logo=google-colab)](https://colab.research.google.com/drive/1p390KHKMQ9xcaDQ7eQTQJjdlX1JTxpmn)

AI-powered educational content generation pipeline that creates complete, age-appropriate science lessons for 9-year-old students (Grade 4). Automatically generates explanations, visuals, quizzes, and activities aligned with Next Generation Science Standards (NGSS).

## 🚀 Live Demo

**[🌟 View Live Demo on Google Colab](https://colab.research.google.com/drive/1p390KHKMQ9xcaDQ7eQTQJjdlX1JTxpmn)**

## ✨ Features

- **🤖 4-Agent Workflow:** Specialized AI agents for research, illustration, writing, and packaging
- **📚 Curriculum-Aligned:** Based on Next Generation Science Standards (NGSS) for Grade 4
- **🎨 Auto-Generated Visuals:** Creates 3 types of educational illustrations (diagrams, fun illustrations, process steps)
- **✍️ Kid-Friendly Content:** 3rd-grade reading level explanations optimized for 9-year-olds
- **📝 Complete Lesson Plans:** Includes teacher guides, student worksheets, quizzes, and answer keys
- **🔍 Web-Powered Research:** Tavily API searches for educational content and fun facts
- **🎯 Interactive Learning:** Quiz questions (5 multiple choice + 2 short answer) and hands-on activities
- **📄 Export Formats:** Markdown and PDF lesson plans ready for classroom use

## 🛠️ Tech Stack

**AI & Processing:**
- **Google Gemini 2.0 Flash** - Content generation and educational analysis
- **Tavily API** - Web search for educational resources
- **Python 3.8+** - Core application logic

**Content Generation:**
- **Natural Language Processing** - Age-appropriate text generation
- **Educational Standards (NGSS)** - Curriculum validation
- **Image Prompt Generation** - Visual illustration design

**Document Processing:**
- **Markdown** - Lesson plan formatting
- **WeasyPrint** - PDF export
- **markdown-it-py** - Markdown to HTML conversion

**Deployment:**
- **Google Colab** - Interactive notebook environment
- **Jupyter Notebook** - Local development

## 🚀 Quick Start

### Prerequisites
- **Google Account** for Google Colab access
- **Gemini API Key** from Google AI Studio
- **Tavily API Key** for web search

### Option 1: Google Colab (Recommended)
```python
# Open the notebook directly in Google Colab
# Click: https://colab.research.google.com/drive/1p390KHKMQ9xcaDQ7eQTQJjdlX1JTxpmn

# Add your API keys to Colab Secrets:
# 1. Click the key icon (🔑) in the left sidebar
# 2. Add: GEMINI_API_KEY and TAVILY_API_KEY
# 3. Run all cells
```

### Option 2: Local Jupyter Notebook
```bash
# Clone the repository
git clone https://github.com/lyven81/ai-project.git
cd ai-project/projects/science-learning-materials-builder

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install google-generativeai tavily-python markdown-it-py weasyprint

# Set up API keys
export GEMINI_API_KEY="your_gemini_api_key"
export TAVILY_API_KEY="your_tavily_api_key"

# Run Jupyter notebook
jupyter notebook science_learning_materials_builder.ipynb
```

## 📖 Usage

### Generate a Complete Lesson

```python
# Generate lesson on any science topic
result = run_science_lesson_pipeline("Photosynthesis")

# View the generated lesson
with open(result["lesson_path"], "r", encoding="utf-8") as f:
    lesson_content = f.read()

# Display in notebook
display(Markdown(lesson_content))

# Export to PDF
pdf_filename = result["lesson_path"].replace(".md", ".pdf")
markdown_to_pdf(lesson_content, pdf_filename)
```

### Supported Science Topics

Based on NGSS Grade 4 Standards:

| Topic | Category | Duration |
|-------|----------|----------|
| **Photosynthesis** | Life Science | 45 min |
| **Water Cycle** | Earth Science | 40 min |
| **Solar System** | Space Science | 50 min |
| **Simple Machines** | Physical Science | 45 min |
| **Food Chains** | Life Science | 40 min |
| **States of Matter** | Physical Science | 40 min |

## 🤖 Multi-Agent Architecture

### Agent 1: Curriculum Research Agent 🔬
**Purpose:** Research topic and validate age-appropriateness

**Workflow:**
1. Searches web for kid-friendly explanations and educational resources
2. Validates against NGSS curriculum standards for Grade 4
3. Extracts 3-5 amazing fun facts suitable for 9-year-olds
4. Suggests hands-on activities and simple experiments
5. Assesses topic appropriateness with reasoning

**Output:**
- Learning objectives in simple language
- Fun facts to engage students
- Recommended lesson duration
- Hands-on activity suggestions

### Agent 2: Visual Illustrator Agent 🎨
**Purpose:** Generate educational illustration prompts

**Workflow:**
1. Creates image generation prompts using Gemini
2. Designs 3 types of educational visuals:
   - **Educational Diagram:** Labeled, clear concept explanation
   - **Fun Illustration:** Cartoon-style, colorful, engaging
   - **Process Steps:** Step-by-step visual guide
3. Ensures bright colors, simple labels, and age-appropriate imagery

**Output:**
- 3 detailed image prompts ready for Imagen/DALL-E
- Captions for each visual
- Image files (or prompts for external generation)

### Agent 3: Content Writer Agent ✍️
**Purpose:** Write lesson content for 9-year-olds

**Workflow:**
1. Creates simple explanation (3-4 paragraphs, 3rd grade reading level)
2. Defines 5 key vocabulary words with kid-friendly definitions
3. Generates quiz questions:
   - 5 multiple choice (4 options each)
   - 2 short answer with sample responses
4. Designs fun challenge activity for home

**Output:**
- Student-friendly explanation with real-world examples
- Vocabulary list with clear definitions
- Complete quiz with answer key
- Creative challenge activity

### Agent 4: Lesson Packaging Agent 📦
**Purpose:** Package everything into a complete lesson plan

**Workflow:**
1. Compiles all agent outputs
2. Creates teacher guide with learning objectives and teaching tips
3. Formats student worksheet with explanations and activities
4. Adds complete answer key
5. Exports to markdown and PDF formats

**Output:**
- Complete lesson plan (markdown)
- Teacher guide with objectives
- Student worksheet
- Answer key
- PDF export ready for printing

## 📚 Lesson Components

### Teacher Guide
- **Learning Objectives:** Clear, measurable goals
- **Key Concepts:** Main ideas to emphasize
- **Teaching Tips:** Helpful suggestions for instruction
- **Materials Needed:** List of required resources

### Student Lesson
- **Explanation:** 3-4 paragraphs at 3rd grade reading level
- **Visual Learning:** 3 educational illustrations with captions
- **Vocabulary:** 5 key terms with kid-friendly definitions
- **Check Your Understanding:** 5 multiple choice + 2 short answer questions
- **Fun Challenge:** Hands-on activity to reinforce learning

### Answer Key
- Complete solutions for all quiz questions
- Sample answers for short response questions
- Assessment rubric guidance

## 📊 Educational Standards Alignment

### Next Generation Science Standards (NGSS) - Grade 4

**Life Science:**
- Photosynthesis and plant processes
- Food chains and energy flow
- Animal and plant adaptations

**Earth Science:**
- Water cycle and weather patterns
- Earth's surface and geological processes

**Physical Science:**
- States of matter and phase changes
- Simple machines and force
- Energy transfer

**Space Science:**
- Solar system and planetary science
- Earth's rotation and orbit

## 🎯 Reading Level & Age-Appropriateness

**Target Audience:** 9-10 year olds (Grade 4)

**Reading Level:** 3rd Grade (Flesch-Kincaid)
- Short sentences (max 15 words)
- Simple vocabulary with clear definitions
- Concrete examples from everyday life
- Engaging, enthusiastic tone

**Visual Design:**
- Bright, cheerful colors
- Simple, clear labels
- No scary or complex imagery
- Cartoon-style illustrations

## 📁 Project Structure

```
science-learning-materials-builder/
├── science_learning_materials_builder.py    # Main Colab notebook (exported)
├── science_learning_materials_builder.ipynb # Jupyter notebook version
├── generated_lessons/                       # Output folder
│   ├── science_lesson_photosynthesis_grade4_20250124.md
│   ├── science_lesson_photosynthesis_grade4_20250124.pdf
│   ├── diagram_photosynthesis.txt
│   ├── fun_illustration_photosynthesis.txt
│   └── process_photosynthesis.txt
├── curriculum_standards/
│   └── ngss_grade4_standards.json
├── requirements.txt
└── README.md
```

## 🧪 Example Output

### Sample Lesson: "How does a cactus survive in the desert?"

**Learning Objectives:**
1. Understand cactus adaptations for water conservation
2. Identify how cacti survive extreme heat
3. Explain the role of spines in protection and water retention

**Fun Facts:**
1. Some cacti can live for over 200 years!
2. Cacti store water in their thick stems like giant water bottles
3. Cactus spines are actually modified leaves
4. The largest cactus can grow taller than a 5-story building
5. Cacti flowers bloom for only 1-2 days per year

**Quiz Sample:**
- Multiple Choice: "Why do cacti have spines instead of leaves?"
  - A. To look pretty
  - B. To reduce water loss ✓
  - C. To attract animals
  - D. To help them grow faster

## 📊 Performance Metrics

- **Generation Time:** 2-3 minutes per complete lesson
- **Content Length:** 1,500-2,000 words
- **Quiz Questions:** 7 per lesson (5 MC + 2 SA)
- **Visual Prompts:** 3 per lesson
- **Reading Level:** 3rd Grade (verified)
- **Export Formats:** Markdown + PDF

## 🔒 Educational Privacy

- **No Student Data Collection:** Focus on content generation only
- **Safe Content:** Age-appropriate verification at every step
- **Curriculum Compliant:** Aligned with established standards
- **Teacher Review:** All lessons should be reviewed before classroom use

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- **More Grade Levels:** Extend to K-3 or 5-8
- **Additional Subjects:** Math, History, Language Arts
- **Interactive Elements:** Embed videos, animations, interactive quizzes
- **Assessment Tools:** Automated grading and progress tracking
- **Multi-Language Support:** Lessons in Spanish, French, Mandarin

## 📝 License

This project is licensed under the MIT License - educational use encouraged!

## 🙏 Acknowledgments

- **Google AI Team** for Gemini 2.0 Flash API
- **Tavily** for educational web search capabilities
- **NGSS Community** for curriculum standards
- **Elementary Education Teachers** for pedagogical insights

## 📧 Contact

- **Portfolio:** [View More Projects](../../README.md)
- **Issues:** [Report Bugs](https://github.com/lyven81/ai-project/issues)

---

⭐ **If you found this project helpful, please give it a star!** ⭐

*Making science education accessible and engaging for every child* 🔬✨
