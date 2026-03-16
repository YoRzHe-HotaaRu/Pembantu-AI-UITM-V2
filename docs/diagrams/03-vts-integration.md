# VTube Studio Integration Architecture

## Overview

The VTube Studio integration provides real-time avatar animation synchronized with TTS audio, including lip sync, gestures, and idle animations.

## VTS Component Architecture

```mermaid
graph TB
    subgraph "VTS Core Module"
        VTS_INIT[VTS Module Init]
        CONN[VTS Connector]
        AUTH[Authentication]
    end

    subgraph "Animation Controllers"
        LIP[Lip Sync Analyzer]
        PLAYER[Lip Sync Player]
        GEST[Gesture Animator]
        IDLE[Idle Animator]
        GC[Gesture Controller]
    end

    subgraph "Supporting Modules"
        AUDIO[Audio Converter]
        EXPRESS[Expression Mapper]
        PARAM[Parameter Manager]
    end

    subgraph "External"
        VTS_APP[VTube Studio App]
        WS[WebSocket :8001]
    end

    VTS_INIT --> CONN
    CONN --> AUTH
    AUTH --> WS
    WS --> VTS_APP

    CONN --> LIP
    CONN --> PLAYER
    CONN --> GEST
    CONN --> IDLE
    CONN --> GC

    LIP --> AUDIO
    PLAYER --> LIP
    GC --> PARAM
    EXPRESS --> PARAM
```

## Connection & Authentication Flow

```mermaid
sequenceDiagram
    participant APP as app.py
    participant VTS as VTSConnector
    participant WS as WebSocket
    participant VTS_APP as VTube Studio

    APP->>VTS: connect()

    Note over VTS,VTS_APP: Step 1: WebSocket Connection
    VTS->>WS: Connect ws://localhost:8001
    WS-->>VTS: Connected

    Note over VTS,VTS_APP: Step 2: Authentication
    alt Has Saved Token
        VTS->>VTS_APP: Authenticate with token
        VTS_APP-->>VTS: Auth Success
    else No Token
        VTS->>VTS_APP: Request New Token
        Note over VTS_APP: Show popup to user
        VTS_APP-->>VTS: User clicks Allow
        VTS_APP-->>VTS: New Token
        VTS->>VTS: Save .vts_token
        VTS->>VTS_APP: Authenticate with new token
        VTS_APP-->>VTS: Auth Success
    end

    Note over VTS,VTS_APP: Step 3: Start Keepalive
    VTS->>VTS: Start keepalive task
    VTS-->>APP: Connection Established
```

## Lip Sync Pipeline

```mermaid
flowchart TD
    A[TTS Audio Generated] --> B[MP3 Audio Data]
    B --> C[Audio Converter]
    C --> D[Convert MP3 to WAV]
    D --> E[Lip Sync Analyzer]

    E --> F[Parse WAV Header]
    F --> G[Extract Audio Samples]
    G --> H[Calculate RMS per Frame]

    H --> I[Apply Threshold]
    I --> J[Apply Smoothing]
    J --> K[Normalize to 0.0-1.0]

    K --> L[Create Timestamp Pairs]
    L --> M[(timestamp, mouth_value)]

    M --> N[Lip Sync Player]
    N --> O[Wait for Frame Time]
    O --> P[Send MouthOpen Parameter]
    P --> Q[VTube Studio API]
    Q --> R[Avatar Mouth Moves]
```

## Complete Animation Flow with TTS

```mermaid
sequenceDiagram
    participant APP as app.py
    participant TTS as Optimized TTS
    participant CONV as Audio Converter
    participant LIP as Lip Sync Analyzer
    participant PLAYER as Lip Sync Player
    participant VTS as VTS Connector
    participant GEST as Gesture Controller
    participant IDLE as Idle Animator
    participant VTS_APP as VTube Studio

    APP->>TTS: generate_audio_streaming(text)

    loop For each TTS chunk
        TTS-->>APP: Audio chunk (MP3)
    end

    APP->>CONV: Convert MP3 to WAV
    CONV-->>APP: WAV bytes

    APP->>LIP: analyze_wav_bytes(wav_data)
    LIP-->>APP: lip_sync_data [(t, mouth_value)]

    APP->>VTS: Check connected
    VTS-->>APP: Connected

    APP->>IDLE: pause()
    APP->>GEST: start_speaking(text, emotion)

    APP->>PLAYER: play_lip_sync(lip_sync_data)

    loop For each frame
        PLAYER->>PLAYER: Wait for timestamp
        PLAYER->>LIP: get_mouth_parameters(value)
        PLAYER->>GEST: get_all_parameters()
        PLAYER->>VTS: set_parameters(all_params)
        VTS->>VTS_APP: Inject param values
    end

    PLAYER-->>APP: Lip sync complete

    APP->>GEST: stop_speaking()
    APP->>IDLE: resume()
```

## Gesture System Architecture

```mermaid
graph TB
    subgraph "Gesture Detection"
        TEXT[Input Text]
        DETECT[Intent Detector]
    end

    subgraph "Gesture Types"
        WAVE[Wave Hello]
        NOD[Nod Agree]
        EXPLAIN[Explain Arm]
        IDLE_W[Idle Waiting]
    end

    subgraph "Gesture Execution"
        HOTKEY[Hotkey Trigger]
        TOGGLE[Toggle State]
        COOLDOWN[Cooldown Check]
    end

    TEXT --> DETECT
    DETECT --> WAVE
    DETECT --> NOD
    DETECT --> EXPLAIN

    WAVE --> HOTKEY
    NOD --> HOTKEY
    EXPLAIN --> TOGGLE
    IDLE_W --> HOTKEY

    HOTKEY --> COOLDOWN
    TOGGLE --> COOLDOWN
```

## Gesture Controller - Body Movement

```mermaid
flowchart LR
    A[Text Input] --> B[Detect Emotion]
    B --> C[Start Speaking State]

    C --> D[Compute Frame Loop]
    D --> E{Calculate Parameters}

    E --> F[Head Movement]
    E --> G[Eye Movement]
    E --> H[Brow Expression]
    E --> I[Body Sway]

    F --> J[ParamHeadAngle]
    G --> K[ParamEyeOpen]
    H --> L[ParamBrow]
    I --> M[ParamBodyRotation]

    J --> N[Merge Parameters]
    K --> N
    L --> N
    M --> N

    N --> O[Send to VTS]
    O --> P{Still Speaking?}
    P -->|Yes| D
    P -->|No| Q[Stop Speaking]
    Q --> R[Ramp Down Activity]
    R --> S[Resume Idle]
```

## Idle Animation System

```mermaid
stateDiagram-v2
    [*] --> Inactive
    Inactive --> Active: Enable

    Active --> Breathing: State = Idle
    Active --> Blinking: Random trigger
    Active --> MicroMovement: Random trigger

    Breathing --> Active: State change
    Blinking --> Breathing: After blink
    MicroMovement --> Breathing: After movement

    Active --> Paused: Pause (talking)
    Paused --> Active: Resume

    Active --> Inactive: Disable
    Inactive --> [*]

    note right of Breathing
        Simulates natural
        breathing pattern
    end note

    note right of Blinking
        Random blink interval
        2-6 seconds
    end note

    note right of MicroMovement
        Small head/body
        movements
    end note
```

## Expression Mapping

```mermaid
graph LR
    subgraph "Emotion Detection"
        AI_TEXT[AI Response Text]
        EMOTION[Emotion Detector]
    end

    subgraph "Detected Emotions"
        HAPPY[Happy]
        NEUTRAL[Neutral]
        SURPRISED[Surprised]
        SAD[Sad]
    end

    subgraph "VTS Expressions"
        EXP1[happy.exp3.json]
        EXP2[neutral.exp3.json]
        EXP3[surprised.exp3.json]
        EXP4[sad.exp3.json]
    end

    AI_TEXT --> EMOTION
    EMOTION --> HAPPY
    EMOTION --> NEUTRAL
    EMOTION --> SURPRISED
    EMOTION --> SAD

    HAPPY --> EXP1
    NEUTRAL --> EXP2
    SURPRISED --> EXP3
    SAD --> EXP4

    EXP1 --> APPLY[Apply Expression]
    EXP2 --> APPLY
    EXP3 --> APPLY
    EXP4 --> APPLY
```

## VTS Parameter Architecture

```mermaid
graph TB
    subgraph "Input Parameters (Tracking)"
        MOUTH_IN[MouthOpen]
        BROW_IN[BrowLeftY]
        EYE_IN[EyeOpenLeft]
    end

    subgraph "Output Parameters (Live2D)"
        MOUTH_OUT[ParamMouthOpenY]
        BROW_OUT[ParamBrowLY]
        EYE_OUT[ParamEyeOpenLeft]
    end

    subgraph "Binding Layer"
        BIND1[Mouth Binding]
        BIND2[Brow Binding]
        BIND3[Eye Binding]
    end

    MOUTH_IN --> BIND1 --> MOUTH_OUT
    BROW_IN --> BIND2 --> BROW_OUT
    EYE_IN --> BIND3 --> EYE_OUT

    Note over MOUTH_IN: API injection point
    Note over MOUTH_OUT: Model control point
```

## Source: `vts/connector.py`

```python
class VTSConnector:
    """WebSocket connector for VTube Studio Plugin API."""

    async def connect(self) -> bool:
        # Connect to WebSocket
        self.websocket = await websockets.connect(uri)

        # Authenticate
        success = await self._authenticate()

        # Ensure mouth parameter exists
        await self._ensure_mouth_parameter()

        # Start keepalive
        self._start_keepalive()

    async def set_parameters(self, parameters: List[Dict]) -> bool:
        """Set multiple parameter values at once."""
        response = await self._send_request(
            "InjectParameterDataRequest",
            {
                "faceFound": True,
                "mode": "set",
                "parameterValues": parameters
            }
        )
        return "errorID" not in response.get("data", {})
```

## Source: `vts/lip_sync.py`

```python
class LipSyncAnalyzer:
    """Analyzes audio waveforms to generate lip sync data."""

    def analyze_wav_bytes(self, wav_data: bytes) -> List[Tuple[float, float]]:
        # Parse WAV header
        sample_rate, audio_samples = self._parse_wav(wav_data)

        # Calculate samples per frame
        samples_per_frame = int(sample_rate / self.target_fps)

        # Generate (timestamp, mouth_value) pairs
        for each frame:
            rms = sqrt(sum(samples^2) / count)  # RMS amplitude
            value = min(1.0, rms * sensitivity)
            value = prev * smoothing + value * (1 - smoothing)
            results.append((timestamp, value))
```

## Source: `vts/gesture_animator.py`

```python
class GestureAnimator:
    """Manages gesture animations via VTube Studio hotkeys."""

    async def trigger_gesture(self, gesture: GestureType, force: bool = False) -> bool:
        # Check cooldown
        if not force and time_since_last_gesture < cooldown:
            return False

        # Handle toggle gestures
        if gesture in toggle_gestures:
            return await self._handle_toggle_gesture(gesture)

        # Trigger hotkey
        return await self._trigger_hotkey(gesture)

    def detect_greeting(self, text: str) -> bool:
        return any(keyword in text for keyword in greeting_keywords)

    def detect_explanation_context(self, text: str) -> bool:
        return any(indicator in text for indicator in explanation_indicators)
```

---

*Generated for UiTM AI Receptionist - VTube Studio Integration Documentation*
