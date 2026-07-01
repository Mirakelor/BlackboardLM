# BlackboardLM

**Your documents, grounded answers.** Upload your materials, ask questions, and get AI-powered insights backed by your sources — like having a research partner who has read everything you've shared.

Built with [Reflex](https://reflex.dev), powered by [Docling](https://github.com/DS4SD/docling) for document parsing and [LightRAG](https://github.com/HKUDS/LightRAG) for knowledge-graph retrieval. Runs with any DeepSeek-compatible API.

---

### 🗺️ Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Uploading Documents](#uploading-documents)
  - [Asking Questions](#asking-questions)
  - [Knowledge Graph](#knowledge-graph)
  - [Preset Modes](#preset-modes)
  - [Query Strategies](#query-strategies)
  - [Themes](#themes)
  - [Settings Panel](#settings-panel)
- [Configuration](#configuration)
- [Prompt System](#prompt-system)
- [License](#license)

---

## Features

### 📎 Grounded Answers with Source Citations

Every answer is anchored in your documents. BlackboardLM reads your uploaded files, builds a knowledge graph, and retrieves the most relevant information for each question. Responses come with inline citations (`[1]`, `[2]`) linking back to your sources, plus a References section and suggested follow-up questions to deepen your exploration.

### 📄 Document Upload & Parsing

Drag and drop PDF, DOCX, PPTX, XLSX, TXT, Markdown, HTML, EPUB, JPG, PNG, or TIFF. Files are automatically parsed, indexed, and turned into a searchable knowledge base. Click any uploaded file to preview its full content rendered as Markdown.

### 🕸️ Knowledge Graph

Every document set generates an interactive knowledge graph showing key entities and their relationships. The graph visualizes the conceptual structure of your materials — click the toggle to expand or collapse it. Nodes are sized by importance and color-coded by entity type.

### 🎛️ 8 Preset Conversation Modes

Quickly shift the AI's approach with one-click presets above the input bar:

| Preset | What it does |
|---|---|
| **Summary** | Comprehensive summary of all documents |
| **Study Guide** | Key concepts, definitions, and review questions |
| **FAQ** | 10–15 essential Q&A pairs from your content |
| **Briefing** | Executive overview of key findings and data |
| **Timeline** | Chronological extraction of key events |
| **Concepts** | Core terminology with definitions and relationships |
| **Critique** | Critical analysis of arguments, gaps, and weak points |
| **Deep Dive** | Exhaustive layered analysis of your question |

### 🔍 5 Retrieval Strategies

Choose how BlackboardLM searches your documents:

| Mode | Behavior |
|---|---|
| **Naive** | Direct full-text answer, no graph retrieval |
| **Local** | Entity-centric: neighbors and related nodes |
| **Global** | Community-level: summary-based retrieval |
| **Hybrid** | Combined local + global |
| **Mix** | All three — naive, local, and global |

### 🎨 Dual Themes

| Theme | Style |
|---|---|
| 🏰 **Flourish & Blotts** | Dark magical-academia aesthetic, parchment textures, candlelight flicker, floating star particles |
| 🌸 **Shiori (栞)** | Light Japanese bookmark-shop aesthetic, muted pinks and greens, falling sakura petals |

Each theme comes with its own color palette, typography, microcopy, and background animations — every text label and placeholder adapts to the theme.

### ⚙️ Settings Panel

A slide-out drawer for live configuration. Change your API key, model, thinking mode, reasoning effort, output length, retrieval strategy, and response style without restarting the app. Settings persist to `.env` and take effect on the next request.

### 🐱 Loading Screen

A CSS-only spinning cat (from hexo-theme-shoka) appears while the knowledge graph initializes. Click to dismiss, or it fades out automatically once your documents are ready.

### 📱 Responsive Layout

Adapts gracefully from desktop to mobile, with a scrollable document shelf, collapsible graph, and fixed bottom input bar.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Reflex](https://reflex.dev) (Tailwind v4, Radix Themes) |
| Document Parsing | [Docling](https://github.com/DS4SD/docling) — PDF, DOCX, PPTX, XLSX, EPUB, HTML, MD, TXT, JPG, PNG, TIFF |
| Knowledge Graph RAG | [LightRAG](https://github.com/HKUDS/LightRAG) + NetworkX + NanoVectorDB |
| LLM | DeepSeek-compatible API (OpenAI SDK) |
| Embedding | `intfloat/multilingual-e5-small` — runs locally, 384-dim, asymmetric |
| Graph Visualization | Cytoscape.js |

---

## 📁 Project Structure

```
BlackboardLM/
├── rxconfig.py                     # Reflex entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── BlackboardLM/
│   ├── BlackboardLM.py             # App entry
│   ├── state.py                    # Global state (Reflex State)
│   ├── config/
│   │   ├── settings.py             # Env loading & .env write-back
│   │   ├── theme.py                # Dual theme definitions
│   │   └── prompts.py              # System prompts & preset modes
│   ├── components/
│   │   ├── layout.py               # Page layout & loading screen
│   │   ├── styles.py               # Global CSS & JS
│   │   ├── header.py               # Nav bar & theme switcher
│   │   ├── settings_panel.py       # Settings drawer
│   │   ├── documents.py            # Upload zone & doc preview
│   │   ├── star_chart.py           # Knowledge graph component
│   │   ├── chat.py                 # Chat message bubbles
│   │   ├── input_bar.py            # Input field & preset chips
│   │   └── decorations.py          # Background particles
│   ├── llm/
│   │   └── client.py               # DeepSeek API client
│   ├── rag/
│   │   └── engine.py               # LightRAG engine wrapper
│   └── pipeline/
│       └── parsers/
│           ├── base.py             # Abstract parser interface
│           └── docling_parser.py   # Docling document parser
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
cd BlackboardLM
pip install -r requirements.txt
```

### 2. Configure your API key

Edit `.env`:

```env
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
LLM_THINKING=disabled
LLM_REASONING_EFFORT=medium
LLM_MAX_TOKENS=16384
QUERY_MODE=naive
```

You can also configure these from the Settings panel after launching.

### 3. Run

```bash
reflex init
reflex run
```

Open `http://localhost:3000`.

---

## Usage

### 📤 Uploading Documents

Drag files directly onto the upload zone at the top of the page, or click it to open your system file picker. You can upload multiple files in one go — they appear as cards in a horizontally scrollable shelf. While a file is being parsed, its card shows a spinner. Once ready, click any card to expand a document preview panel with the full Markdown-rendered content, including extracted tables.

Supported formats: PDF, DOCX, PPTX, XLSX, TXT, Markdown, HTML, EPUB, JPG, PNG, TIFF.

Behind the scenes, each uploaded file is parsed, its entities and relationships are extracted into a knowledge graph, and the full text is chunked and indexed for retrieval — all automatically.

### 💬 Asking Questions

Type your question and press **Enter** (use **Shift+Enter** for newlines). BlackboardLM retrieves relevant passages from your documents and generates an answer grounded in your sources. Each response includes:

- **Inline citations** — `[1]`, `[2]` linking to your documents
- **References** — a list of cited sources at the end
- **Dive Deeper** — 3–5 suggested follow-up questions

The conversation carries context across turns, so you can drill deeper naturally.

### 🕸️ Knowledge Graph

After documents are processed, an interactive knowledge graph appears below the upload shelf. It visualizes the concepts and entities extracted from your files, connected by the relationships discovered between them. Use the chevron button on the title bar to collapse or expand the graph. The graph is rendered with Cytoscape.js — you can pan and zoom to explore dense clusters. Nodes are sized by their connection count (degree) and color-coded by entity type. Hover over a node to see its full description; edges show the keyword linking two entities.

When no documents are loaded, the graph area shows a placeholder message. While documents are parsing, it displays a processing indicator. Both adapt to the active theme.

### 🎛️ Preset Modes

Eight preset chips are positioned above the input bar, collapsed by default. Click **"Presets ▸"** to reveal them, then click any chip to activate that mode. The selected chip highlights in the theme's primary color. Click it again to deselect and return to the default conversation style. Only one preset can be active at a time.

Each preset injects a specific instruction into the system prompt, shaping how the AI structures its response. For example, **Study Guide** adds "create a study guide with key concepts, definitions, and review questions"; **Timeline** asks for chronological event extraction. The presets are defined in `config/prompts.py` under `PRESET_MODES`.

### 🔍 Query Strategies

Control how BlackboardLM retrieves information from your documents via the **Query Mode** dropdown in Settings. The default is **Naive** (direct full-text retrieval, bypassing the knowledge graph). Switch to **Local**, **Global**, **Hybrid**, or **Mix** when you want graph-aware answers that leverage entity relationships and community summaries. The choice persists in `.env` under `QUERY_MODE`.

### 🎨 Themes

Two theme chips sit in the top navigation bar: **🏰 Flourish & Blotts** (dark magical-academia) and **🌸 Shiori** (light Japanese). Click either to switch instantly — colors, fonts, background particles, button styles, and all microcopy change together. The active theme is saved to `.env` (`THEME=sakura` or `THEME=hogwarts`) and restored on next launch.

All theme data lives in `config/theme.py` as two `Theme` dataclass instances. Adding a new theme means creating a third instance and registering it in `header.py`.

### ⚙️ Settings Panel

Click the gear icon in the header to open the settings drawer. Configure your API key, model, thinking mode, reasoning depth, output token limit, retrieval strategy, and response style. Changes are saved to `.env` and applied on the next request — no restart needed.

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DEEPSEEK_API_KEY` | — | Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API endpoint |
| `LLM_MODEL` | `deepseek-chat` | Model name |
| `LLM_THINKING` | `disabled` | Deep thinking mode (`enabled` / `disabled`) |
| `LLM_REASONING_EFFORT` | `medium` | Reasoning depth (`low` / `medium` / `high` / `max`) |
| `LLM_MAX_TOKENS` | `16384` | Max output tokens |
| `QUERY_MODE` | `naive` | Default retrieval strategy |
| `THEME` | `sakura` | Default theme (`sakura` / `hogwarts`) |

All values can be changed at runtime via the Settings panel.

### HuggingFace Mirror

On startup, BlackboardLM checks connectivity to `huggingface.co`. If unreachable (e.g., from mainland China), it automatically sets `HF_ENDPOINT=https://hf-mirror.com` so the embedding model can still be downloaded.

---

## 🧠 Prompt System

The system prompt is assembled from modular blocks in `config/prompts.py`:

```
Role & Goal          → "You are BlackboardLM, an AI research assistant..."
Deep Analysis        → Multi-angle thinking before answering
Comprehensiveness    → Detailed, structured, well-elaborated answers
Grounding            → Primary: document sources. Secondary: general knowledge. Always distinguish.
Citations            → Inline [n] + References section (max 5)
Dive Deeper          → 3–5 follow-up questions at the end
Formatting           → Rich Markdown, reply in user's language
Constraints          → No one-line answers, no fabrication, always close with a summary
Preset Instruction   → (Optional) The selected preset mode's specific directive
```

The `naive` mode receives raw document chunks as `{content_data}`; all other modes receive knowledge-graph context as `{context_data}`.

---

## 📄 License

MIT
