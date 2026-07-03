# BlackboardLM

**Your documents, grounded answers.** Upload your materials, ask questions, and get AI-powered insights backed by your sources — like having a research partner who has read everything you've shared.

Built with [Reflex](https://reflex.dev), powered by [MarkitDown](https://github.com/microsoft/markitdown) for document parsing and a browser-side LightRAG Web Worker for knowledge-graph RAG. No Node.js required — bring your own DeepSeek-compatible API key. Model files are downloaded directly from HuggingFace by the browser.

---

### 🗺️ Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Deploy to Reflex Cloud](#-deploy-to-reflex-cloud)
- [Usage](#usage)
  - [Authentication](#authentication)
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

Every answer is anchored in your documents. BlackboardLM reads your uploaded files, builds a knowledge graph, and retrieves the most relevant information for each question. The system prompt instructs the model to provide inline citations (`[1]`, `[2]`), a References section, and suggested follow-up questions to deepen your exploration.

### 📄 Document Upload & Parsing

Drag and drop PDF, DOCX, PPTX, XLSX, TXT, Markdown, HTML, EPUB, JPG, PNG, TIFF, CSV, JSON, or XML. Files are automatically parsed by MarkitDown on the Python backend, then indexed by the browser-side LightRAG engine into a searchable knowledge base. Click any uploaded file to preview its full content rendered as Markdown.

### 🕸️ Knowledge Graph

Every document set generates an interactive knowledge graph showing key entities and their relationships. The graph visualizes the conceptual structure of your materials — click the toggle to expand or collapse it. Nodes are sized by importance and color-coded by entity type. Graph data persists via IndexedDB and is restored on page reload.

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
| **Naive** | Direct LLM answer, no retrieval — chat mode |
| **Local** | Vector search over document chunks |
| **Global** | Knowledge graph entity summaries |
| **Hybrid** | Combined local + global |
| **Mix** | All three — naive, local, and global |

### 🎨 Dual Themes

| Theme | Style |
|---|---|
| 🏰 **Flourish & Blotts** | Dark magical-academia aesthetic, parchment textures, candlelight flicker, floating star particles |
| 🌸 **栞 (Shiori)** | Light Japanese bookmark-shop aesthetic, muted pinks and greens, falling sakura petals |

Each theme comes with its own color palette, typography, microcopy, and background animations — every text label and placeholder adapts to the theme.

### 🔐 Authentication

Set `ACCESS_PASSWORD` in your `.env` or deployment environment to enable password protection. When configured, a login card appears before the main interface. Enter the password to unlock the app — a persistent cookie keeps you logged in across page refreshes, so you only need to enter it once per browser session.

When no password is set, the app opens directly without authentication — ideal for local development. A **Logout** button in the Settings panel lets you sign out and return to the login screen.

### ⚙️ Settings Panel

A slide-out drawer for live configuration. Change your API key, base URL, model, thinking mode, reasoning effort, output length, retrieval strategy, and response style without restarting the app. Settings persist to `.env` and take effect on the next request.

A **Clear All Data** button resets everything — knowledge graph, indexed documents, chat history, cached previews, and dedup records — returning the app to a fresh state. When authentication is enabled, a **Logout** button is also available.

### 🐱 Loading Screen

A CSS-only spinning cat (from hexo-theme-shoka) appears while the knowledge graph initializes. Click to dismiss, or it fades out automatically once your documents are ready.

### 📱 Responsive Layout

Adapts gracefully from desktop to mobile, with a scrollable document shelf, collapsible graph, and fixed bottom input bar.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Reflex](https://reflex.dev) (Tailwind v4, Radix Themes) |
| Document Parsing | [MarkitDown](https://github.com/microsoft/markitdown) — 15 formats (PDF, DOCX, PPTX, XLSX, EPUB, HTML, MD, TXT, JPG, JPEG, PNG, TIFF, CSV, JSON, XML) |
| Knowledge Graph RAG | Browser-side Web Worker (LightRAG architecture), in-memory graph + vector DB, IndexedDB persistence |
| LLM | DeepSeek-compatible API, called directly from browser via `fetch` |
| Embedding | `Xenova/multilingual-e5-small` via Transformers.js (WASM), 384-dim. Model files downloaded directly from HuggingFace by the browser |
| Graph Visualization | Cytoscape.js, loaded from unpkg CDN |
| Vector DB | In-memory cosine similarity (lightrag built-in) |

---

## 📁 Project Structure

```
BlackboardLM/
├── rxconfig.py                     # Reflex entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables
├── assets/
│   ├── favicon.ico
│   ├── rag.worker.js               # LightRAG + Transformers.js Web Worker
│   └── rag_bridge.js               # Main-thread bridge (Worker ↔ Reflex state)
├── BlackboardLM/
│   ├── BlackboardLM.py             # App entry
│   ├── state.py                    # Global state & bridge event handlers
│   ├── config/
│   │   ├── settings.py             # Env loading, defaults, .env write-back
│   │   ├── theme.py                # Dual theme definitions
│   │   └── prompts.py              # System prompts & preset modes
│   ├── components/
│   │   ├── layout.py               # Page layout, hidden bridge divs
│   │   ├── styles.py               # Global CSS & JS (Cytoscape, bridge loader)
│   │   ├── header.py               # Nav bar & theme switcher
│   │   ├── settings_panel.py       # Settings drawer
│   │   ├── auth.py                 # Login card
│   │   ├── documents.py            # Upload zone & doc preview
│   │   ├── star_chart.py           # Knowledge graph component
│   │   ├── chat.py                 # Chat message bubbles
│   │   ├── input_bar.py            # Input field & preset chips
│   │   └── decorations.py          # Background particles
│   ├── rag/
│   │   └── engine.py               # LLM config provider
│   └── pipeline/
│       └── parsers/
│           ├── base.py             # Abstract parser interface
│           └── markitdown_parser.py # MarkitDown document parser
└── lightrag/
    ├── package.json
    ├── server.js                   # Node.js entry (for standalone/CLI use)
    └── src/
        ├── index.js                # Node.js exports
        ├── lightrag.js             # Core RAG engine
        ├── vector_db.js            # In-memory cosine-similarity vector DB
        ├── graph.js                # Knowledge graph
        ├── chunker.js              # Token-based text chunker
        ├── embedder.js             # Transformers.js embedding wrapper
        ├── prompts.js              # Entity extraction prompt
        └── storage.js              # IndexedDB persistence (browser)
```

---

## 🚀 Getting Started

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

Edit `.env`:

```env
DEEPSEEK_API_KEY=sk-your-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

All other settings have sensible defaults and can be changed via the Settings panel.

### 3. Run

```bash
reflex init
reflex run
```

Open `http://localhost:3000` (dev mode). In production, the app runs on a single port (`http://localhost:8000`).

On first launch, the embedding model (~470 MB) is downloaded directly from HuggingFace. The model is cached by your browser for instant reuse on subsequent loads. A progress indicator shows download and indexing status.

---

## ☁️ Deploy to Reflex Cloud

Reflex Cloud deploys your app to Fly.io behind a custom domain in one command. No Docker, no CI/CD, no YAML.

### Prerequisites

- [Fork this repository](https://github.com/Mirakelor/BlackboardLM/fork) to your own GitHub account
- A [Reflex Cloud](https://reflex.dev) account
- `reflex` CLI installed (`pip install reflex`) and authenticated:

```bash
reflex login
```

This opens your browser to sign in with GitHub or Google. After login, go to the [Reflex Cloud dashboard](https://cloud.reflex.dev), create a new project, and copy the `reflex deploy` command — it contains your project's access token:

```bash
reflex deploy --project <your-project-id>
```

### Step 1 — Set your password

Open `rxconfig.py` and set a login password for your app:

```python
os.environ.setdefault("ACCESS_PASSWORD", "your-password-here")
```

Leave it `""` to skip authentication.

### Step 2 — Deploy

Run the deploy command from the Cloud dashboard:

```bash
reflex deploy --project <your-project-id>
```

Press Enter at the interactive prompts. The CLI compiles your app, uploads it, and the build continues in the background. You can close the terminal once the upload finishes.

### Step 3 — Configure your API key

Once deployed, open your app and click the gear icon in the header to open the **Settings** panel. Fill in your `DEEPSEEK_API_KEY` and click **Save & Apply** — settings take effect immediately, no restart needed.

You can also set environment variables from the Cloud dashboard under **Settings** → **API Keys**, or pass them at deploy time with `--env`:

```bash
reflex deploy --project <id> --env DEEPSEEK_API_KEY=sk-your-key
```

### Step 4 — Update your app

After making code changes, simply run `reflex deploy --project <your-project-id>` again. Settings configured through the in-app panel persist across deploys — only code changes require a re-deploy.

> **Note:** The embedding model (`Xenova/multilingual-e5-small`, ~470 MB) is downloaded directly from HuggingFace by each user's browser on first visit. No server bandwidth cost for model serving.

---

## Usage

### 📤 Uploading Documents

Drag files directly onto the upload zone at the top of the page, or click it to open your system file picker. You can upload multiple files in one go — they appear as cards in a horizontally scrollable shelf. While a file is being parsed, its card shows a spinner. Once ready, click any card to expand a document preview panel with the full Markdown-rendered content, including tables.

Supported formats: PDF, DOCX, PPTX, XLSX, TXT, Markdown, HTML, EPUB, JPG, JPEG, PNG, TIFF, CSV, JSON, XML.

Behind the scenes: the Python backend parses each document with MarkitDown, sends the text to the browser, and the LightRAG Web Worker chunks, embeds, and extracts entities — all while showing live progress.

### 💬 Asking Questions

Type your question and press **Enter** (use **Shift+Enter** for newlines). The browser-side LightRAG engine retrieves relevant context from your documents, then calls the LLM API directly for a streaming answer. Each response includes:

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

Control how BlackboardLM retrieves information from your documents via the **Query Mode** dropdown in Settings. The default is **Naive** (sends your question directly to the LLM with no retrieval — fast, lightweight chat mode). Switch to **Local** for vector search over document chunks, **Global** for knowledge graph entity summaries, **Hybrid** for both, or **Mix** for all three combined. The choice persists in `.env` under `QUERY_MODE`.

### 🎨 Themes

Two theme chips sit in the top navigation bar: **🏰 Flourish & Blotts** (dark magical-academia) and **🌸 栞** (light Japanese). Click either to switch instantly — colors, fonts, background particles, button styles, and all microcopy change together. The active theme is read from the `THEME` env var on startup and defaults to `sakura`.

All theme data lives in `config/theme.py` as two `Theme` dataclass instances. Adding a new theme means creating a third instance, adding it to `THEMES` dict, updating the conditional in `layout._main_app()`, and registering a switch chip in `header.py`.

### ⚙️ Settings Panel

Click the gear icon in the header to open the settings drawer. Configure your API key, model, thinking mode, reasoning depth, output token limit, retrieval strategy, and response style. Changes are saved to `.env` and applied on the next request — no restart needed.

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ACCESS_PASSWORD` | `""` | Login password (empty = no auth) |
| `DEEPSEEK_API_KEY` | — | Your DeepSeek API key |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API endpoint |
| `LLM_MODEL` | `deepseek-v4-flash` | Model name |
| `LLM_THINKING` | `disabled` | Deep thinking mode |
| `LLM_REASONING_EFFORT` | `max` | Reasoning depth (`low` / `medium` / `high` / `max`) |
| `LLM_MAX_TOKENS` | `16384` | Max output tokens |
| `QUERY_MODE` | `naive` | Default retrieval strategy |
| `RESPONSE_TYPE` | `Multiple Paragraphs` | Response formatting style |
| `THEME` | `sakura` | Default theme (`sakura` / `hogwarts`) |
All values can be changed at runtime via the Settings panel.

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

When a preset is selected, its instruction is appended as an additional directive.
```

Context is injected by the browser-side lightrag engine — vector chunks for local/hybrid/mix modes, knowledge graph entities for global/hybrid/mix modes. The `{response_type}` placeholder in the prompt is formatted at query time from the Settings value.

---

## 📄 License

MIT
