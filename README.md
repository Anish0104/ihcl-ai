# IHCL AI — Staff Intelligence Suite
Proof of Concept | Built by Anish Shirodkar | MS Computer Science, Rutgers University

A multi-property AI staff intelligence platform demonstrating the same RAG architecture working across two IHCL properties: The Pierre, New York (luxury flagship) and amã Stays Serenity Bungalow, Coorg (boutique heritage property).

## Properties
- The Pierre, A Taj Hotel — luxury flagship, Fifth Avenue, New York City
- amã Stays Serenity Bungalow, Coorg — boutique heritage plantation property, Karnataka, India

## Features
1. Staff Co-pilot: RAG-powered Q&A over real property knowledge. Switch between properties — same architecture, different knowledge base and persona.
2. Guest Brief Generator: Input guest details, receive a structured pre-arrival brief tailored to each property type.
3. Guest Support (amã Stays only): Simplified guest-facing 24/7 support interface — the 11pm solution when no staff is on site.

## Setup
1. Clone and create virtual environment: `python3.12 -m venv venv && source venv/bin/activate`
2. Install: `pip install -r backend/requirements.txt`
3. Copy `.env.example` to `.env` and add your `GROQ_API_KEY` (free at `console.groq.com`)
4. Ingest knowledge base: `cd backend && python ingest.py`
5. Run: `uvicorn backend.main:app --reload --port 8000`
6. Open `http://localhost:8000`, enter password: `ihcl2024`

## Proof of Concept Boundary
Running on public data only. Pierre version uses data from `thepierreny.com`. amã Stays version uses curated property data. The production version would connect to IHCL's PMS, CRM, and Azure Data Lake for real guest history, live availability, and booking system integration. That connection is what the internship is for.

## Tech Stack
Backend: Python, FastAPI, ChromaDB, sentence-transformers, Groq API (LLaMA 3.3 70B)
Frontend: Single HTML file, vanilla JS, Google Fonts
Deployment: Render.com
