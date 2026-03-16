# Data Flow Sequence Diagrams

## Overview

This document provides detailed sequence diagrams for the main data flows in the UiTM AI Receptionist system.

---

## 1. Complete User Query Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend JS
    participant BE as Flask Backend
    participant RAG as RAG Manager
    participant AI as OpenRouter API
    participant TTS as TTS Service
    participant VTS as VTube Studio

    rect rgb(200, 220, 255)
        Note over U,VTS: Phase 1: User Input
        U->>FE: Type question & press Enter
        FE->>FE: Disable input field
        FE->>FE: Add user message to chat
        FE->>FE: Show "AI thinking..." indicator
    end

    rect rgb(220, 255, 200)
        Note over U,VTS: Phase 2: Backend Processing
        FE->>BE: POST /api/chat {message, model}
        BE->>RAG: query(message, top_k=5)
        RAG->>RAG: Search knowledge base
        RAG-->>BE: {context, sources, chunks}
    end

    rect rgb(255, 230, 200)
        Note over U,VTS: Phase 3: AI Generation
        BE->>AI: POST /chat/completions (stream)
        AI-->>BE: Stream: reasoning tokens
        BE-->>FE: SSE: reasoning_update
        FE->>FE: Expand reasoning panel
        FE->>U: Show live reasoning

        AI-->>BE: Stream: content tokens
        BE-->>FE: SSE: content_update
        FE->>FE: Append content to message
        FE->>U: Stream text display

        AI-->>BE: Stream complete
    end

    rect rgb(255, 255, 200)
        Note over U,VTS: Phase 4: Response Finalization
        BE->>BE: Format response
        BE-->>FE: SSE: stream_end
        FE->>FE: Store message in state
        FE->>FE: Enable input field
        FE->>FE: Hide "AI thinking..."
        FE->>U: Show complete response
    end

    rect rgb(255, 220, 240)
        Note over U,VTS: Phase 5: TTS & Animation (Optional)
        alt TTS Enabled
            FE->>BE: POST /api/tts {text}
            BE->>TTS: generate_audio_streaming(text)
            TTS-->>BE: Stream MP3 chunks
            BE-->>FE: Audio chunks

            FE->>FE: Buffer & play audio
            FE->>FE: Convert MP3 to WAV
            FE->>FE: Analyze lip sync data
            FE->>VTS: Send mouth parameters
            VTS->>VTS: Animate avatar mouth
            VTS->>U: Avatar speaks
        end
    end
```

---

## 2. RAG Query Flow

```mermaid
sequenceDiagram
    autonumber
    participant BE as Backend
    participant RM as RAG Manager
    participant DL as Document Loader
    participant SR as Simple Retriever
    participant HR as Hybrid Retriever
    participant VS as Vector Store

    BE->>RM: query(user_question)

    alt Advanced Mode
        RM->>HR: retrieve(query, top_k)
        HR->>VS: semantic_search(query_embedding)
        VS-->>HR: Similar chunks (semantic)
        HR->>HR: Combine with keyword search
        HR-->>RM: Ranked chunks
    else Lightweight Mode
        RM->>SR: retrieve(query, top_k)
        SR->>DL: keyword_search(query)
        DL-->>SR: Matched documents
        SR->>SR: Score & rank chunks
        SR-->>RM: Ranked chunks
    end

    RM->>RM: Format context string
    RM->>RM: Extract unique sources
    RM-->>BE: {context, sources, chunks}
```

---

## 3. TTS Audio Generation Flow

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant BE as Backend
    participant TTS as OptimizedMinimaxTTS
    participant CACHE as TTS Cache
    participant WS as Minimax WebSocket
    participant CONV as Audio Converter
    participant LIP as Lip Sync Analyzer

    FE->>BE: Request TTS for text

    BE->>TTS: generate_audio_streaming(text)
    TTS->>CACHE: Check cache

    alt Cache Hit
        CACHE-->>TTS: Return cached MP3
        TTS-->>BE: Complete audio
    else Cache Miss
        TTS->>TTS: Split into sentences

        loop For each sentence
            TTS->>WS: task_start + task_continue
            WS-->>TTS: Stream audio chunks
            TTS->>TTS: Accumulate audio
        end

        TTS->>CACHE: Store complete audio
        TTS-->>BE: Stream MP3 chunks
    end

    BE->>CONV: Convert MP3 to WAV
    CONV-->>BE: WAV bytes

    BE->>LIP: analyze_wav_bytes(wav_data)
    LIP-->>BE: [(timestamp, mouth_value)]

    BE-->>FE: Audio stream + lip_sync_data
```

---

## 4. VTube Studio Connection Flow

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant BE as Backend
    participant VTS as VTS Connector
    participant TOKEN as .vts_token File
    participant WS as VTube Studio WebSocket

    FE->>BE: Enable VTS in settings
    BE->>VTS: connect()

    VTS->>WS: WebSocket connect ws://localhost:8001
    WS-->>VTS: Connected

    alt Has Saved Token
        VTS->>TOKEN: Read auth token
        TOKEN-->>VTS: Return token
        VTS->>WS: Authenticate with token
        WS-->>VTS: Auth success
    else No Token
        VTS->>WS: Request authentication token
        Note over WS: Show popup in VTS UI
        WS-->>VTS: User must click Allow
        WS-->>VTS: Return new token
        VTS->>TOKEN: Save token
        VTS->>WS: Authenticate with new token
        WS-->>VTS: Auth success
    end

    VTS->>VTS: Start keepalive task
    VTS-->>BE: Connection established
    BE-->>FE: VTS connected successfully
```

---

## 5. Gesture Animation Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend
    participant GEST as Gesture Animator
    participant GC as Gesture Controller
    participant VTS as VTS Connector
    participant IDLE as Idle Animator

    U->>FE: Send message "Hello!"
    FE->>GEST: detect_greeting(text)
    GEST->>GEST: Check keyword list
    GEST-->>FE: Greeting detected

    FE->>GEST: trigger_gesture(WAVE_HELLO)
    GEST->>GEST: Check cooldown
    GEST->>VTS: trigger_hotkey("wave_hello")
    VTS->>VTS: Play hotkey animation
    VTS-->>GEST: Success
    GEST-->>FE: Gesture triggered

    rect rgb(200, 220, 255)
        Note over U,IDLE: During AI Response
        FE->>GEST: detect_explanation_context(ai_text)
        GEST-->>FE: Explanation detected

        FE->>GEST: trigger_gesture(EXPLAIN_ARM)
        GEST->>GEST: Toggle ON
        GEST->>VTS: trigger_hotkey("explain_arm")
        VTS-->>GEST: Arm gesture ON

        FE->>GC: start_speaking(text, emotion)
        GC->>GC: Detect emotion from text
        GC->>GC: Start body movement loop
        GC->>VTS: Continuous param updates

        loop While speaking
            GC->>GC: Compute frame (head, body, eyes)
            GC->>VTS: set_parameters()
        end

        FE->>GC: stop_speaking()
        GC->>GC: Ramp down activity
        GC-->>FE: Stopped
        FE->>GEST: disable_toggle(EXPLAIN_ARM)
        GEST->>VTS: trigger_hotkey() again (OFF)
        FE->>IDLE: resume()
    end
```

---

## 6. Idle Animation System Flow

```mermaid
stateDiagram-v2
    [*] --> Disabled: VTS disabled

    Disabled --> Initializing: Enable requested
    Initializing --> Connected: Auth success
    Connected --> IdleActive: Enable idle

    IdleActive --> Breathing: Start breathing cycle
    Breathing --> BlinkWait: Breathing complete
    BlinkWait --> Blinking: Random blink trigger
    Blinking --> MicroWait: Blink complete
    MicroWait --> MicroMovement: Random movement trigger
    MicroMovement --> Breathing: Movement complete

    IdleActive --> Paused: TTS started (pause)
    Paused --> IdleActive: TTS ended (resume)

    IdleActive --> Disabled: Disable requested

    note right of Breathing
        3-second cycle
        subtle chest/head
        movement
    end note

    note right of Blinking
        Random interval
        2-6 seconds
        natural blink speed
    end note

    note right of MicroMovement
        Small head tilt
        body sway
        eye movement
    end note
```

---

## 7. Theme Switching Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend
    participant STORAGE as localStorage

    U->>FE: Click theme toggle button

    FE->>STORAGE: getItem('uitm-theme')
    STORAGE-->>FE: Return current theme

    alt Current is 'light'
        FE->>FE: Set theme = 'dark'
        FE->>FE: Update CSS variables
        FE->>FE: Apply .theme-dark class
        FE->>STORAGE: setItem('uitm-theme', 'dark')
    else Current is 'dark'
        FE->>FE: Set theme = 'light'
        FE->>FE: Update CSS variables
        FE->>FE: Apply .theme-light class
        FE->>STORAGE: setItem('uitm-theme', 'light')
    end

    FE->>FE: Re-render UI with new theme
```

---

## 8. Quick Access Flow (Mobile)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend
    participant BE as Backend

    U->>FE: Tap "Quick Access" panel (mobile)
    FE->>FE: Display categories

    loop For each category
        FE->>FE: Show category header
        FE->>FE: List FAQ questions
    end

    U->>FE: Tap FAQ question
    FE->>FE: Set as input value
    FE->>FE: Auto-submit question
    FE->>BE: POST /api/chat {message}

    Note over FE,BE: Continue with standard chat flow
```

---

## 9. Error Handling Flow

```mermaid
flowchart TD
    A[API Request] --> B{Request Success?}
    B -->|Yes| C[Process Response]
    B -->|No| D[Error Handler]

    D --> E{Error Type?}
    E -->|Network| F[Show "Connection Error"]
    E -->|API Key| G[Show "API Not Configured"]
    E -->|VTS| H[Show "VTS Unavailable"]
    E -->|TTS| I[Fallback: Text Only]

    F --> J[Log Error]
    G --> J
    H --> J
    I --> K[Disable TTS Flag]

    J --> L[Re-enable Input]
    K --> L
    C --> L
```

---

## 10. Performance Metrics Collection

```mermaid
sequenceDiagram
    autonumber
    participant FE as Frontend
    participant PERF as Perf Monitor
    participant BE as Backend

    FE->>FE: Record start_time

    FE->>BE: Send chat request
    BE-->>FE: First token received
    FE->>PERF: Record time_to_first_token

    loop Streaming
        BE-->>FE: Content chunk
        FE->>PERF: Record tokens_received
    end

    BE-->>FE: Stream complete
    FE->>PERF: Record total_response_time

    PERF->>PERF: Calculate tokens/sec
    PERF->>PERF: Update metrics display

    FE->>FE: Show perf monitor overlay
```

---

*Generated for UiTM AI Receptionist - Data Flow Documentation*
