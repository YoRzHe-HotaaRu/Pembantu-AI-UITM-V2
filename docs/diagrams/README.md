# UiTM AI Receptionist - Architecture Documentation Index

Welcome to the architecture documentation for the UiTM AI Receptionist chatbot system.

## 📑 Table of Contents

| # | Document | Description |
|---|----------|-------------|
| 01 | [System Architecture](./01-system-architecture.md) | High-level system overview, component architecture, directory structure |
| 02 | [RAG System](./02-rag-system.md) | Retrieval-Augmented Generation system architecture and flow |
| 03 | [VTube Studio Integration](./03-vts-integration.md) | Avatar animation, lip sync, and gesture system |
| 04 | [TTS Pipeline](./04-tts-pipeline.md) | Text-to-Speech pipeline with Minimax API |
| 05 | [Frontend-Backend Interaction](./05-frontend-backend.md) | API endpoints, state management, UI components |
| 06 | [Data Flow Sequences](./06-data-flow-sequences.md) | Detailed sequence diagrams for main data flows |

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         UiTM AI Receptionist                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   Frontend   │────▶│    Backend   │────▶│  AI Services │            │
│  │  (Browser)   │     │   (Flask)    │     │  (OpenRouter)│            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │     Theme    │     │    RAG System│     │  TTS Service │            │
│  │   State Mgmt │     │  (Knowledge) │     │   (Minimax)  │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                    │                    │                     │
│         ▼                    ▼                    ▼                     │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │    Mobile    │     │  Vector Store│     │ VTube Studio │            │
│  │   Panels     │     │   (Cache)    │     │   (Avatar)   │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Components

### Frontend (`static/`)
- **styles.css** - Swedish geometry design system
- **app.js** - State management, API calls, UI logic

### Backend (`app.py`)
- Flask application with streaming endpoints
- OpenRouter API integration
- RAG system integration
- TTS and VTS coordination

### RAG System (`rag/`)
- **rag_manager.py** - Main orchestrator
- **document_loader.py** - Markdown, JSON, PDF parsing
- **retriever.py** - Hybrid retrieval (keyword + semantic)
- **simple_retriever.py** - Lightweight keyword retrieval

### VTube Studio Integration (`vts/`)
- **connector.py** - WebSocket connection & authentication
- **lip_sync.py** - Audio analysis for mouth movement
- **gesture_animator.py** - Hotkey-based gesture triggering
- **gesture_controller.py** - Continuous body/head movement
- **idle_animator.py** - Breathing, blinking, micro-movements

### TTS Service (`tts_optimized.py`)
- Persistent WebSocket connections
- Sentence-level chunking
- Parallel processing
- Audio caching

---

## 🚀 Quick Start

### For Developers
1. Read [System Architecture](./01-system-architecture.md) for overview
2. Review [Data Flow Sequences](./06-data-flow-sequences.md) for request flows
3. Check specific component docs for implementation details

### For New Team Members
1. Start with [Frontend-Backend Interaction](./05-frontend-backend.md)
2. Review [RAG System](./02-rag-system.md) for knowledge base info
3. Explore [TTS Pipeline](./04-tts-pipeline.md) for audio features

### For VTS Integration
1. Read [VTube Studio Integration](./03-vts-integration.md) completely
2. Check parameter binding requirements
3. Review gesture system configuration

---

## 📊 Architecture Diagrams Summary

### Mermaid Diagrams Included

| Document | Diagrams |
|----------|----------|
| 01 | High-Level Architecture, Component Architecture, Directory Structure, Data Flow Overview, Module Dependencies |
| 02 | RAG Component Architecture, Document Loading Process, Query Processing Flow, Two-Mode Retrieval, Initialization Sequence, Chunking Flow |
| 03 | VTS Component Architecture, Connection Flow, Lip Sync Pipeline, Animation Flow, Gesture System, Gesture Controller, Idle Animation, Expression Mapping, Parameter Architecture |
| 04 | TTS Component Architecture, Request Flow, Sentence Chunking, WebSocket Protocol, Persistent WS State, Parallel Processing, Caching System, Configuration |
| 05 | API Endpoints, Chat Flow, Streaming Protocol, State Management, UI Components, Theme System, Mobile Panels, Settings Modal, SSE Handling |
| 06 | Complete User Query, RAG Query, TTS Generation, VTS Connection, Gesture Animation, Idle Animation, Theme Switching, Quick Access, Error Handling, Performance Metrics |

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys, feature flags) |
| `requirements.txt` | Python dependencies |
| `.vts_token` | VTube Studio authentication token |
| `static/js/app.js` | Frontend configuration and state |
| `app.py` | Backend configuration (models, voices, etc.) |

---

## 📁 Related Documentation

- **Main README**: `../README.md` - Installation and usage guide
- **API Documentation**: See backend code comments in `app.py`
- **VTS Documentation**: `../vts_parameter_info/` - Parameter reference
- **Knowledge Base**: `../knowledge_base/` - UiTM information data

---

## 📝 Document Maintenance

When updating the codebase, consider updating these diagrams if:
- New components are added
- Data flow changes
- New API endpoints are created
- Architecture patterns change
- New integrations are added

---

*Last updated: 2026-03-15*
*Generated for UiTM AI Receptionist - System Documentation*
