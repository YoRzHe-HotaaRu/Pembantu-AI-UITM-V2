# Frontend-Backend Interaction

## Overview

This document describes the communication patterns between the frontend (browser) and backend (Flask) components of the UiTM AI Receptionist.

## API Endpoints

```mermaid
graph TB
    subgraph "Frontend Routes"
        HOME[/]
        CHAT[/api/chat]
        CHAT_STREAM[/api/chat/stream]
        SETTINGS[/api/settings]
        VTS_STATUS[/api/vts/status]
    end

    subgraph "Backend Handlers"
        INDEX[render_template]
        CHAT_HDL[chat_handler]
        STREAM_HDL[stream_handler]
        CONFIG[config_handler]
        STATUS[status_handler]
    end

    HOME --> INDEX
    CHAT --> CHAT_HDL
    CHAT_STREAM --> STREAM_HDL
    SETTINGS --> CONFIG
    VTS_STATUS --> STATUS
```

## Complete Chat Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend (app.js)
    participant BE as Backend (Flask)
    participant RAG as RAG System
    participant AI as OpenRouter API
    participant TTS as TTS Service
    participant VTS as VTube Studio

    U->>FE: Type message, press Enter
    FE->>FE: Add user message to chat
    FE->>FE: Show "AI thinking..." state
    FE->>BE: POST /api/chat {message, model}

    BE->>BE: Build system prompt
    BE->>RAG: Query knowledge base
    RAG-->>BE: Context + sources
    BE->>AI: POST chat completion (stream)
    AI-->>BE: Stream reasoning tokens
    BE-->>FE: SSE: reasoning_update
    FE->>FE: Update reasoning panel

    AI-->>BE: Stream content tokens
    BE-->>FE: SSE: content_update
    FE->>FE: Append to message
    FE->>FE: Highlight code blocks

    AI-->>BE: Stream complete
    BE->>BE: Check for special responses
    BE-->>FE: SSE: stream_end {content, reasoning}

    FE->>FE: Store message in state
    FE->>FE: Update UI state
    FE->>U: Display final response

    opt TTS Enabled
        FE->>BE: POST /api/tts {text}
        BE->>TTS: Generate audio
        TTS-->>BE: Audio stream
        BE-->>FE: Audio chunks
        FE->>FE: Play audio
        FE->>VTS: Send lip sync data
    end
```

## Message Streaming Protocol

```mermaid
flowchart TD
    A[Connection Open] --> B{Event Type?}

    B -->|reasoning_update| C[Update Reasoning Panel]
    B -->|content_update| D[Append to Content]
    B -->|stream_end| E[Finalize Message]
    B -->|error| F[Show Error]

    C --> G{More Events?}
    D --> G
    G -->|Yes| B
    G -->|No| H[Stream Complete]

    E --> H
    F --> H

    H --> I[Enable Input]
    I --> J[Trigger TTS if enabled]
```

## State Management Architecture

```mermaid
graph TB
    subgraph "Core State"
        MESSAGES[messages: Array]
        TYPING[isTyping: boolean]
        PANEL[currentPanel: string]
        THEME[theme: string]
    end

    subgraph "AI State"
        MODEL[model: string]
        REASONING[currentReasoning: string]
        CONTENT[currentContent: string]
        RAG_USED[ragUsed: boolean]
    end

    subgraph "TTS State"
        TTS_ENABLED[ttsEnabled: boolean]
        AUDIO_STATE[audio: Object]
    end

    subgraph "VTS State"
        VTS_ENABLED[vts.enabled: boolean]
        VTS_CONNECTED[vts.connected: boolean]
        VTS_LIPSYNC[vts.lipSyncData: Array]
    end

    subgraph "Settings State"
        SETTINGS_MODAL[settings.isOpen: boolean]
        PERF_MONITOR[perfMonitor.enabled: boolean]
    end
```

## UI Component Interactions

```mermaid
graph LR
    subgraph "Input Components"
        TEXTAREA[Message Textarea]
        SEND_BTN[Send Button]
        QUICK[Quick Access Items]
    end

    subgraph "Display Components"
        CHAT_BOX[Chat Container]
        REASONING[Reasoning Panel]
        SOURCES[Sources Panel]
    end

    subgraph "Control Components"
        THEME_TOGGLE[Theme Toggle]
        PANEL_TOGGLE[Panel Toggle]
        SETTINGS_BTN[Settings Button]
        TTS_TOGGLE[TTS Toggle]
        VTS_TOGGLE[VTS Toggle]
    end

    TEXTAREA --> SEND_BTN
    SEND_BTN --> CHAT_BOX
    QUICK --> TEXTAREA
    CHAT_BOX --> REASONING
    CHAT_BOX --> SOURCES

    THEME_TOGGLE --> CHAT_BOX
    PANEL_TOGGLE --> CHAT_BOX
    SETTINGS_BTN --> SETTINGS_MODAL
    TTS_TOGGLE --> AUDIO_STATE
    VTS_TOGGLE --> VTS_STATE
```

## Theme System

```mermaid
flowchart LR
    A[Theme Toggle Click] --> B{Current Theme?}
    B -->|Light| C[Switch to Dark]
    B -->|Dark| D[Switch to Light]

    C --> E[Update CSS Variables]
    D --> E

    E --> F[Save to localStorage]
    F --> G[Apply Theme Class]

    H[Page Load] --> I[Read localStorage]
    I --> J{Theme Saved?}
    J -->|Yes| K[Apply Saved Theme]
    J -->|No| L[Default to Light]
```

## Mobile Panel System

```mermaid
stateDiagram-v2
    [*] --> Desktop: Width >= 1024px
    Desktop --> Mobile: Width < 1024px

    Mobile --> QuickAccess: Default state
    QuickAccess --> ChatPanel: Tap "Chat" button
    ChatPanel --> QuickAccess: Tap "Quick Access" button

    Desktop --> [*]
    Mobile --> [*]

    note right of QuickAccess
        Shows FAQ categories
        and quick questions
    end note

    note right of ChatPanel
        Full-width chat
        with message input
    end note
```

## Settings Modal Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant BE as Backend

    U->>FE: Click Settings Button
    FE->>FE: Open Modal
    FE->>BE: GET /api/settings

    BE-->>FE: Current config

    U->>FE: Change TTS setting
    FE->>FE: Update local state
    FE->>BE: POST /api/settings {tts: true/false}

    BE->>BE: Update config
    BE-->>FE: Success

    U->>FE: Change Model
    FE->>FE: Update state.model
    FE->>BE: POST /api/settings {model: new_model}

    U->>FE: Toggle VTS
    FE->>FE: Update vts.enabled
    FE->>BE: POST /api/vts/connect

    alt VTS Available
        BE->>VTS: Connect
        VTS-->>BE: Connected
        BE-->>FE: Success
    else VTS Unavailable
        BE-->>FE: Error
    end

    U->>FE: Close Modal
    FE->>FE: Hide Modal
```

## Event Source (SSE) Handling

```javascript
// Frontend SSE handler (simplified from app.js)

function startChatStream(message, model) {
    const eventSource = new EventSource(`/api/chat/stream?message=${encodeURIComponent(message)}&model=${model}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch(data.type) {
            case 'reasoning_update':
                state.currentReasoning += data.content;
                updateReasoningDisplay();
                break;

            case 'content_update':
                state.currentContent += data.content;
                updateMessageDisplay();
                break;

            case 'stream_end':
                eventSource.close();
                finalizeMessage(data);
                if (state.ttsEnabled) {
                    triggerTTS(state.currentContent);
                }
                break;

            case 'error':
                eventSource.close();
                showError(data.message);
                break;
        }
    };
}
```

## Backend Route Handlers

```python
# Flask routes (simplified from app.py)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    model = data.get('model', DEFAULT_MODEL)

    # Query RAG for context
    rag_result = rag_manager.query(message, top_k=5)

    # Build messages for AI
    messages = build_prompt(message, rag_result['context'])

    # Call OpenRouter API
    response = call_openrouter(messages, model)

    return jsonify({
        'response': response['content'],
        'reasoning': response['reasoning'],
        'sources': rag_result['sources']
    })

@app.route('/api/chat/stream', methods=['GET'])
def chat_stream():
    message = request.args.get('message')
    model = request.args.get('model', DEFAULT_MODEL)

    def generate():
        # Stream from OpenRouter
        for chunk in stream_openrouter(message, model):
            if chunk.type == 'reasoning':
                yield f"data: {json.dumps({'type': 'reasoning_update', 'content': chunk.content})}\n\n"
            elif chunk.type == 'content':
                yield f"data: {json.dumps({'type': 'content_update', 'content': chunk.content})}\n\n"

        yield f"data: {json.dumps({'type': 'stream_end'})}\n\n"

    return Response(generate(), mimetype='text/event-stream')
```

## Keyboard Shortcuts

```
┌─────────────────────────────────────────────────────┐
│ Keyboard Shortcuts                                  │
├─────────────────────────────────────────────────────┤
│ Enter           │ Send message                      │
│ Shift + Enter   │ New line in textarea              │
│ Escape          │ Close modal / Cancel              │
│ Ctrl + K        │ Focus search/quick access         │
│ Ctrl + T        │ Toggle theme                      │
│ Ctrl + ,        │ Open settings                     │
└─────────────────────────────────────────────────────┘
```

---

*Generated for UiTM AI Receptionist - Frontend-Backend Interaction Documentation*
