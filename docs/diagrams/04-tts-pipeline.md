# TTS Pipeline Architecture

## Overview

The Text-to-Speech (TTS) system uses Minimax API with optimized streaming, persistent WebSocket connections, and parallel processing for low-latency audio generation.

## TTS Component Architecture

```mermaid
graph TB
    subgraph "TTS Interface"
        APP[app.py]
        GET_TTS[get_tts_instance]
        OPT_TTS[OptimizedMinimaxTTS]
    end

    subgraph "Core Processing"
        SPLIT[Sentence Splitter]
        STREAM[Streaming Generator]
        PARALLEL[Parallel Processor]
    end

    subgraph "WebSocket Layer"
        PERSISTENT[Persistent WS]
        WS_POOL[Connection Pool]
        SSL[SSL Context]
    end

    subgraph "Caching"
        CACHE[TTSCache]
        DISK[File-based Storage]
    end

    APP --> GET_TTS
    GET_TTS --> OPT_TTS
    OPT_TTS --> SPLIT
    OPT_TTS --> STREAM
    OPT_TTS --> PARALLEL
    STREAM --> PERSISTENT
    PARALLEL --> WS_POOL
    PERSISTENT --> SSL
    OPT_TTS --> CACHE
    CACHE --> DISK
```

## TTS Request Flow

```mermaid
sequenceDiagram
    participant APP as app.py
    participant STATE as state.currentContent
    participant TTS as OptimizedMinimaxTTS
    participant CACHE as TTS Cache
    participant WS as Minimax WebSocket
    participant CONV as Audio Converter
    participant LIP as Lip Sync Analyzer

    APP->>STATE: Receive AI response text
    APP->>TTS: generate_audio_streaming(text)

    alt Cache Hit
        TTS->>CACHE: Get cached audio
        CACHE-->>TTS: MP3 bytes
        TTS-->>APP: Cached chunk
    else Cache Miss
        TTS->>TTS: Split into sentences

        loop For each sentence chunk
            TTS->>WS: task_start + task_continue
            WS-->>TTS: Stream audio chunks
            TTS->>CACHE: Cache complete audio
        end

        TTS-->>APP: Audio chunks (MP3)
    end

    APP->>CONV: MP3 to WAV conversion
    CONV-->>APP: WAV bytes

    APP->>LIP: analyze_wav_bytes()
    LIP-->>APP: lip_sync_data
```

## Sentence Chunking Strategy

```mermaid
flowchart TD
    A[Input Text] --> B{Length > 200 chars?}

    B -->|No| C[Single Chunk]
    B -->|Yes| D[Split by Sentences]

    D --> E{Sentence > 200?}
    E -->|No| F[Use Sentence Chunks]
    E -->|Yes| G[Split by Commas]

    G --> H{Still Too Long?}
    H -->|Yes| I[Hard Split at 200]
    H -->|No| J[Use Comma Chunks]

    C --> K[Process Chunk]
    F --> K
    J --> K
    I --> K

    K --> L{More Chunks?}
    L -->|Yes| M[Next Chunk]
    L -->|No| N[All Chunks Ready]

    M --> K
```

## WebSocket Communication Protocol

```mermaid
sequenceDiagram
    participant TTS as OptimizedMinimaxTTS
    participant MM as Minimax API

    Note over TTS,MM: Connection Phase
    TTS->>MM: WebSocket Connect
    MM-->>TTS: connected_success event

    Note over TTS,MM: Task Initialization
    TTS->>MM: task_start event
    Note over TTS,MM: model, voice_setting, audio_setting
    MM-->>TTS: task_started event

    Note over TTS,MM: Text Submission
    TTS->>MM: task_continue event
    Note over TTS,MM: text content

    Note over TTS,MM: Audio Streaming
    loop Until Complete
        MM-->>TTS: audio chunk (hex encoded)
        TTS->>TTS: Decode hex to bytes
    end

    MM-->>TTS: is_final: true

    Note over TTS,MM: Cleanup
    TTS->>MM: task_finish event
    TTS->>MM: WebSocket Close
```

## Persistent WebSocket Optimization

```mermaid
stateDiagram-v2
    [*] --> Disconnected

    Disconnected --> Connecting: Request audio
    Connecting --> Connected: WebSocket established
    Connected --> Active: task_start sent
    Active --> Streaming: task_continue sent
    Streaming --> Complete: is_final received
    Complete --> Connected: task_finish sent
    Connected --> Idle: No activity

    Idle --> Active: New request (< 30s)
    Idle --> Disconnected: Timeout (> 30s)

    note right of Idle
        Persistent connection
        kept alive for 30s
        for faster response
    end note
```

## Parallel Processing Architecture

```mermaid
graph TB
    subgraph "Input Text"
        TEXT[Full Response Text]
    end

    subgraph "Sentence Splitting"
        S1[Sentence 1]
        S2[Sentence 2]
        S3[Sentence 3]
        S4[...]
        SN[Sentence N]
    end

    subgraph "Thread Pool Execution"
        W1[Worker 1: S1]
        W2[Worker 2: S2]
        W3[Worker 3: S3]
        W4[Worker 4: S4]
    end

    subgraph "WebSocket Tasks"
        WS1[WS Connection 1]
        WS2[WS Connection 2]
        WS3[WS Connection 3]
        WS4[WS Connection 4]
    end

    subgraph "Result Collection"
        R1[Result 1]
        R2[Result 2]
        R3[Result 3]
        R4[Result 4]
    end

    subgraph "Output"
        MERGED[Merged Audio Stream]
    end

    TEXT --> S1
    TEXT --> S2
    TEXT --> S3
    TEXT --> S4
    TEXT --> SN

    S1 --> W1
    S2 --> W2
    S3 --> W3
    S4 --> W4

    W1 --> WS1
    W2 --> WS2
    W3 --> WS3
    W4 --> WS4

    WS1 --> R1
    WS2 --> R2
    WS3 --> R3
    WS4 --> R4

    R1 --> MERGED
    R2 --> MERGED
    R3 --> MERGED
    R4 --> MERGED
```

## Audio Caching System

```mermaid
flowchart LR
    A[Text Input] --> B[Generate Cache Key]
    B --> C[MD5 Hash]

    C --> D{Check Cache File}
    D -->|Exists| E[Read Cached MP3]
    D -->|Not Found| F[Generate TTS]

    E --> G[Return Cached Audio]
    F --> H[Cache New Audio]
    H --> G

    I[voice_id] --> B
    J[model] --> B
    K[text] --> B
```

## TTS Configuration Options

```mermaid
graph TB
    subgraph "Model Settings"
        MODEL[Model: speech-2.8-turbo]
        VOICE[Voice: Malay_male_1_v1]
        LANG[Language: Malay]
    end

    subgraph "Audio Settings"
        SAMPLE[Sample Rate: 32000 Hz]
        BITRATE[Bitrate: 128000 kbps]
        FORMAT[Format: MP3]
        CHANNEL[Channel: 1 (Mono)]
    end

    subgraph "Voice Settings"
        SPEED[Speed: 1.0]
        VOLUME[Volume: 1.0]
        PITCH[Pitch: 0]
    end

    subgraph "Pronunciation"
        TONE[Tone: uitm/UITM]
    end
```

## Source: `tts_optimized.py`

```python
class OptimizedMinimaxTTS:
    """Optimized Minimax TTS with persistent WebSocket and caching."""

    async def generate_audio_streaming(
        self,
        text: str,
        on_chunk: Optional[Callable[[TTSChunk], None]] = None
    ) -> AsyncGenerator[TTSChunk, None]:
        # Check cache first
        if self.cache:
            cached = self.cache.get(text, self.config["voice_id"], self.config["model"])
            if cached:
                yield TTSChunk(audio_bytes=cached, text=text, is_last=True)
                return

        # Split into sentences
        sentences = self.split_into_sentences(text)

        if len(sentences) == 1:
            # Single sentence - streaming
            async for chunk in self._generate_single_sentence_streaming(...):
                yield chunk
        else:
            # Multiple sentences - parallel processing
            async for chunk in self._generate_parallel_sentences(sentences, ...):
                yield chunk
```

## Source: Audio Converter (`vts/audio_converter.py`)

```python
class AudioConverter:
    """Converts MP3 audio to WAV format for lip sync analysis."""

    @staticmethod
    def mp3_to_wav(mp3_bytes: bytes) -> bytes:
        """
        Convert MP3 to WAV using ffmpeg.

        Args:
            mp3_bytes: MP3 audio data

        Returns:
            WAV audio data
        """
        # Create temp files
        mp3_path = f"temp_input_{timestamp}.mp3"
        wav_path = f"temp_output_{timestamp}.wav"

        # Write MP3
        with open(mp3_path, 'wb') as f:
            f.write(mp3_bytes)

        # Run ffmpeg conversion
        subprocess.run([
            'ffmpeg', '-i', mp3_path,
            '-ar', '32000',  # 32kHz sample rate
            '-ac', '1',     # Mono
            wav_path
        ])

        # Read WAV
        with open(wav_path, 'rb') as f:
            wav_bytes = f.read()

        # Cleanup temp files
        os.remove(mp3_path)
        os.remove(wav_path)

        return wav_bytes
```

## Performance Metrics

```
TTS Pipeline Timing (typical):
├── Cache lookup: <1ms
├── Sentence splitting: <5ms
├── WebSocket connection: 50-200ms (if not persistent)
├── First audio chunk: 200-500ms
├── Full audio generation: 1-3 seconds
├── MP3 to WAV conversion: 100-300ms
└── Lip sync analysis: 50-100ms

With persistent WebSocket:
- Connection overhead eliminated
- Response time improved by 50-200ms
```

---

*Generated for UiTM AI Receptionist - TTS Pipeline Documentation*
