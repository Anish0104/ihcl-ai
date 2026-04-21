# IHCL AI — Staff Intelligence Suite
Proof of Concept | Built by Anish Shirodkar | MS Computer Science, Rutgers University

IHCL AI is a multi-property staff intelligence demo built for an interview with the VP of Artificial Intelligence at IHCL, part of the Tata Group. It demonstrates a simple but important enterprise idea:

the same RAG platform, the same LLM, and the same user experience can support very different hospitality operations by switching the property-specific knowledge base, assistant persona, and output structure.

This proof of concept is intentionally grounded in two contrasting IHCL properties:

- The Pierre, A Taj Hotel, New York: a luxury flagship hotel where the assistant behaves like a polished staff co-pilot for concierge, front desk, dining, events, and hotel policy questions.
- amã Stays & Trails, Serenity Bungalow, Coorg: a boutique heritage estate where the assistant shifts into a warmer, more practical support role for guest guide questions, local recommendations, and after-hours property help.

## Why This Demo Matters
- It shows how one AI platform can scale across IHCL's portfolio without rebuilding the product for every property.
- It makes the gap explicit between public-data RAG and the full production opportunity: PMS, CRM, booking systems, loyalty history, and operational data.
- It demonstrates multiple AI interaction patterns in one workflow:
  - Staff co-pilot Q&A
  - Pre-arrival guest brief generation
  - Guest-facing support for off-hours operational questions

## Core Demo Insight
The star of the demo is the property switcher.

When the user switches from The Pierre to amã Stays:

- the knowledge base changes
- the assistant persona changes
- the answer tone changes
- the suggested prompts change
- the brief-generation format changes
- the Guest Support tab appears only for amã

That is the architectural pitch: one scalable AI operating layer for many IHCL brands and property types.

## Features
### 1. Staff Co-pilot
RAG-powered question answering over curated property knowledge.

- The Pierre version handles hotel overview, dining, policies, event spaces, FAQ, and Upper East Side concierge guidance.
- amã version handles property overview, guest guide, local area support, and FAQ content for Serenity Bungalow, Coorg.
- Every answer includes source tags.
- The assistant clearly refuses guest-history, booking, PMS, or live-availability questions outside the public-data boundary.

### 2. Guest Brief Generator
Structured pre-arrival brief generation using Groq and property-specific prompting.

- The Pierre brief includes:
  - Front Desk
  - Concierge
  - Food & Beverage
  - Housekeeping
  - Welcome Letter
- The amã brief includes:
  - Property Setup
  - Meal Preparation
  - Local Recommendations
  - Welcome Note
- Allergy and dietary notes are flagged prominently for operational visibility.

### 3. Guest Support
Available only for amã Stays.

- Designed for the "11 PM problem" when a guest needs help and staff are not immediately beside them.
- Covers WiFi, power cuts, wildlife safety, meal timing, local medical access, and other practical guest-guide scenarios.

## Tech Stack
### Backend
- Python
- FastAPI
- ChromaDB
- sentence-transformers
- Groq Python SDK
- LLaMA 3.3 70B via Groq free API

### Frontend
- Single-file HTML
- Vanilla JavaScript
- Inline CSS
- SSE streaming for chat responses

### Deployment Target
- Render.com

## Model and Retrieval Stack
### LLM
- Provider: Groq
- Model: `llama-3.3-70b-versatile`
- Use cases:
  - streaming chat completion
  - non-streaming brief generation

### Retrieval
- Vector store: ChromaDB
- Embeddings: `all-MiniLM-L6-v2` through `sentence-transformers`
- Collections:
  - `pierre_knowledge`
  - `ama_knowledge`

The two collections are fully separate. Pierre queries do not retrieve amã content, and amã queries do not retrieve Pierre content.

## Project Structure
```text
ihcl-ai/
├── data/
│   ├── pierre/
│   │   ├── pierre_hotel.md
│   │   ├── pierre_dining.md
│   │   ├── pierre_events.md
│   │   ├── pierre_policies.md
│   │   ├── pierre_faq.md
│   │   └── neighbourhood.md
│   └── ama/
│       ├── ama_overview.md
│       ├── ama_guestguide.md
│       ├── ama_local.md
│       └── ama_faq.md
├── backend/
│   ├── main.py
│   ├── rag.py
│   ├── brief.py
│   ├── prompts.py
│   ├── ingest.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── .env.example
└── README.md
```

## Quick Start
### 1. Create and activate a virtual environment
```bash
python3.12 -m venv venv
source venv/bin/activate
```

If `python3.12` is not available on your machine, use `python3`.

### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Add environment variables
Copy the example file:

```bash
cp .env.example .env
```

Then set:

```env
GROQ_API_KEY=your_groq_api_key_here
APP_PASSWORD=ihcl2024
```

You can get a free Groq API key from `console.groq.com`.

### 4. Ingest the knowledge base
```bash
python backend/ingest.py
```

This builds the Pierre and amã ChromaDB collections from the markdown source files.

### 5. Run the app
```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://localhost:8000
```

Login password:

```text
ihcl2024
```

## Demo Flow
If you are presenting this in an interview, this sequence lands well:

1. Start with The Pierre in Staff Co-pilot mode.
2. Ask a service-oriented question such as:
   `What live music is available at Two E?`
3. Ask a concierge-style question such as:
   `What can the concierge arrange for a guest?`
4. Switch to amã Stays and point out that the same app now behaves differently.
5. Ask:
   `What if the power goes out at night?`
6. Open Guest Support and ask:
   `I saw a large animal outside`
7. Open Guest Brief Generator and create one Pierre brief and one amã brief to show the property-specific output format.

## Sample Questions
### The Pierre
- `What time does Perrine close?`
- `What is the capacity of the Cotillion Room?`
- `Can dogs stay at the hotel?`
- `What subway stop is closest to the hotel?`
- `What can the concierge arrange for a guest?`

### amã Stays
- `What is included in the stay?`
- `What if the power goes out at night?`
- `Is the WiFi reliable enough for video calls?`
- `Where is the nearest hospital?`
- `What should I do if I see a large animal outside?`

## API Endpoints
### `GET /`
Serves the single-file frontend.

### `GET /api/health`
Returns service health plus whether `GROQ_API_KEY` is configured.

### `POST /api/chat`
Streaming chat endpoint using Server-Sent Events.

Request body:
- `messages`
- `property`
- `password`

### `POST /api/brief`
Generates a structured guest brief using the selected property's prompt template.

Request body:
- `guest_data`
- `property`
- `password`

## Proof of Concept Boundary
This app is intentionally constrained.

### Included
- Public or curated property knowledge
- Retrieval over markdown knowledge bases
- AI-generated answers and structured briefs
- Property-specific assistant personas and workflows

### Not Included
- Real guest history
- PMS data
- CRM data
- Live inventory or booking availability
- Reservation modifications
- Real-time operational systems integration

The UI and prompts explicitly call out this limitation because that integration layer is the next-stage product opportunity.

## Notes for Reviewers
- This is a demo application, not a production deployment.
- The Pierre content is based on publicly available property information.
- The amã Stays content is curated to simulate a guest-guide and local-support workflow.
- The product intentionally shows where enterprise data connections would deepen usefulness across IHCL's broader portfolio.

## Repository Notes
- `.env` is ignored and should never be committed.
- `chroma_db/` is generated locally after ingestion and is not required to understand the codebase.
- The frontend is intentionally kept in a single HTML file for speed of iteration and demo portability.

## Author
Anish Shirodkar  
MS Computer Science, Rutgers University
