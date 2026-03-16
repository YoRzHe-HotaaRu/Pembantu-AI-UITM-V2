# System Architecture Overview

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[HTML/CSS/JS Interface]
        THEME[Theme Controller]
        PANEL[Panel Manager]
        STATE[State Management]
    end

    subgraph "Backend Layer - Flask"
        FLASK[Flask Application]
        ROUTES[API Routes]
        STREAM[Streaming Handler]
    end

    subgraph "AI Services"
        OR[OpenRouter API]
        RAG[RAG System]
        TTS[TTS Service]
    end

    subgraph "VTube Studio Integration"
        VTS_CONN[VTS Connector]
        LIP[Lip Sync Analyzer]
        GEST[Gesture Animator]
        IDLE[Idle Animator]
    end

    subgraph "Data Layer"
        KB[Knowledge Base]
        CACHE[TTS Cache]
        VTS_TOKEN[.vts_token]
    end

    UI --> FLASK
    FLASK --> OR
    FLASK --> RAG
    FLASK --> TTS
    FLASK --> VTS_CONN
    VTS_CONN --> LIP
    VTS_CONN --> GEST
    VTS_CONN --> IDLE
    RAG --> KB
    TTS --> CACHE
    VTS_CONN --> VTS_TOKEN
```

## Component Architecture

```mermaid
graph LR
    subgraph "Client Browser"
        A[User Interface]
        B[JavaScript Controller]
        C[WebSocket Client]
    end

    subgraph "Flask Server :5000"
        D[app.py Main Entry]
        E[Chat Endpoint]
        F[Streaming Endpoint]
        G[Settings Endpoint]
    end

    subgraph "External Services"
        H[OpenRouter API]
        I[Minimax TTS API]
        J[VTube Studio :8001]
    end

    A --> B
    B --> E
    B --> F
    B --> G
    E --> D
    F --> D
    G --> D
    D --> H
    D --> I
    D --> J
```

## Directory Structure

```
uitm-chatbot/
│
├── app.py                      # Main Flask application
├── minimax_tts.py              # Legacy TTS module
├── tts_optimized.py            # Optimized streaming TTS
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
│
├── static/
│   ├── css/
│   │   └── styles.css          # Swedish geometry design
│   ├── js/
│   │   └── app.js              # Frontend logic
│   └── assets/
│       └── logo_uitm.png       # UiTM logo
│
├── templates/
│   └── index.html              # Main UI template
│
├── rag/                        # RAG System
│   ├── __init__.py
│   ├── rag_manager.py          # Main RAG orchestrator
│   ├── document_loader.py      # Document parsing
│   ├── chunker.py              # Text chunking
│   ├── embeddings.py           # Embedding generation
│   ├── vector_store.py         # Vector database
│   ├── retriever.py            # Hybrid retriever
│   ├── simple_retriever.py     # Keyword retriever
│   └── image_handler.py        # Image retrieval
│
├── vts/                        # VTube Studio Integration
│   ├── __init__.py
│   ├── connector.py            # WebSocket connector
│   ├── lip_sync.py             # Audio analysis
│   ├── gesture_animator.py     # Gesture system
│   ├── gesture_controller.py   # Body movement
│   ├── idle_animator.py        # Idle animations
│   ├── audio_converter.py      # MP3 to WAV
│   └── expressions.py          # Emotion mapping
│
├── knowledge_base/
│   ├── 02-admissions/          # Admission info
│   ├── 03-campus/              # Campus facilities
│   ├── 04-administrative/      # Admin info
│   └── assets/                 # KB images
│
├── tts_cache/                  # TTS audio cache
├── rag_cache/                  # RAG embeddings cache
└── vts_parameter_info/         # VTS parameter docs
```

## Data Flow Overview

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend JS
    participant BE as Flask Backend
    participant RAG as RAG System
    participant AI as OpenRouter AI
    participant TTS as TTS Service
    participant VTS as VTube Studio

    U->>FE: Type message & press Enter
    FE->>BE: POST /chat (message)
    BE->>RAG: Query knowledge base
    RAG-->>BE: Context + sources
    BE->>AI: Send prompt + context
    AI-->>BE: Stream response
    BE-->>FE: Stream chunks
    FE->>U: Display reasoning
    FE->>U: Display response
    FE->>BE: Request TTS
    BE->>TTS: Generate audio
    TTS-->>BE: Audio stream
    BE-->>FE: Audio chunks
    FE->>VTS: Lip sync data
    Note over VTS: Avatar speaks
```

## Module Dependencies

```mermaid
graph TD
    APP[app.py] --> RAG_M[RAG Manager]
    APP --> TTS_OPT[Optimized TTS]
    APP --> VTS_CONN[VTS Connector]
    APP --> IMG_H[Image Handler]

    RAG_M --> DOC_L[Document Loader]
    RAG_M --> SIMP_R[Simple Retriever]
    RAG_M --> HYB_R[Hybrid Retriever]

    TTS_OPT --> CACHE[TTS Cache]
    TTS_OPT --> WS[WebSocket Client]

    VTS_CONN --> LIP[Lip Sync]
    VTS_CONN --> GEST[Gesture]
    VTS_CONN --> IDLE[Idle]

    DOC_L --> MD[Markdown Parser]
    DOC_L --> JSON[JSON Parser]
    DOC_L --> PDF[PDF Parser]
```

---

*Generated for UiTM AI Receptionist - System Documentation*
