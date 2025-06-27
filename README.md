# AI Newsletter Curation Agent

An intelligent newsletter curation system that automatically fetches, analyzes, and curates AI and technology news using the Strands SDK and Ollama.

## Features

- 🤖 **AI-Powered Curation**: Uses local LLM (Qwen2.5) via Ollama for intelligent article analysis
- 📡 **Multi-Source Aggregation**: Fetches from 6+ major tech news RSS feeds
- 🔍 **Smart Filtering**: Automatically filters content based on AI/tech relevance
- 📝 **Markdown Output**: Generates clean, formatted newsletters in markdown
- 🔧 **Tool-Based Architecture**: Built with Strands SDK for extensible agent workflows
- 🏠 **Privacy-First**: Runs entirely locally with Ollama

## Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running

### Installation

1. Clone the repository:
\`\`\`bash
git clonehttps://github.com/ScottBiggs2/Ollama-Strands-SDK-Newsletter-Agent.git
cd Ollama-Strands-SDK-Newsletter-Agent
\`\`\`

2. Create virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Start Ollama and download model:
\`\`\`bash
ollama serve
ollama pull qwen2.5:3b
\`\`\`

5. Run the agent:
\`\`\`bash
python main.py
\`\`\`

## How It Works

1. **Fetches articles** from major tech news RSS feeds
2. **Filters content** using AI/tech keyword matching
3. **Analyzes articles** with local LLM for relevance and quality
4. **Generates newsletter** in clean markdown format
5. **Saves output** to \`ai_tech_newsletter.md\`

## Configuration

Edit the \`NewsletterConfig\` class in \`main.py\` to:
- Add/remove RSS sources
- Modify keyword filters
- Adjust article limits
- Change model parameters

## Tech Stack

- **Strands SDK**: Agent framework with tool calling
- **Ollama**: Local LLM inference
- **Qwen2.5**: 3B parameter model with tool support
- **BeautifulSoup**: Web scraping
- **Feedparser**: RSS feed processing

## License

MIT License - see LICENSE file for details.
