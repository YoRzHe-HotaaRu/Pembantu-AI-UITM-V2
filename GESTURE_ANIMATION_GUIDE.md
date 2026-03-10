# Gesture Animation System Guide

## Overview
The gesture animation system allows the VTube Studio avatar to play specific animations based on user input and AI responses. Animations are triggered via VTube Studio hotkeys.

## Available Gestures

| Gesture Name | Hotkey ID | Trigger Condition | Type |
|--------------|-----------|-------------------|------|
| `wave_hello` | `wave_hello` | User says hello/greetings | One-shot |
| `nod_head_agree` | `nod_head_agree` | User asks for confirmation/agreement | One-shot |
| `explain_arm_gesture` | `explain_arm_gesture` | AI is explaining a topic seriously | Toggle (on/off) |
| `explain_hand_left` | `explain_hand_left` | AI is explaining with left hand point | One-shot |
| `explain_hand_right` | `explain_hand_right` | AI is explaining with right hand point | One-shot |
| `idle_waiting` | `idle_waiting` | Randomly change idle animation | One-shot |

## How It Works

### 1. User Input Detection
When a user sends a message, the system automatically detects:
- **Greetings**: "hello", "hi", "hey", "assalamualaikum", "selamat pagi", etc.
- **Agreement**: "yes", "yeah", "correct", "betul", "setuju", etc.

If detected, the corresponding gesture is triggered immediately.

### 2. AI Response Detection
When the AI responds, the system detects:
- **Explanation context**: "let me explain", "here's how", "begini", "mari saya terangkan", etc.

If detected, the `explain_arm_gesture` is toggled ON during the response and automatically turned OFF after completion.

### 3. Toggle Gestures
The `explain_arm_gesture` is a toggle-type animation:
- First trigger: Animation turns ON
- Second trigger: Animation turns OFF
- Auto-off: Automatically disabled 1 second after AI response completes

## API Endpoints

### Trigger Specific Gesture
```
POST /vts/trigger_gesture
{
    "gesture": "wave_hello",
    "force": false
}
```

### Auto-Detect and Trigger
```
POST /vts/detect_and_trigger
{
    "text": "Hello there!",
    "source": "user"  // or "ai"
}
```

### Disable Explain Gesture
```
POST /vts/disable_explain_gesture
```

### Get Gesture Status
```
GET /vts/gesture_status
```

## Frontend JavaScript Functions

```javascript
// Trigger a specific gesture
triggerVTSGesture('wave_hello');

// Auto-detect and trigger from text
detectAndTriggerGesture('Hello!', 'user');

// Disable explain gesture
disableExplainGesture();

// Get gesture status
getGestureStatus();
```

## VTube Studio Setup

1. Open VTube Studio
2. Go to **Hotkeys** settings
3. Create hotkeys with these exact IDs:
   - `wave_hello`
   - `nod_head_agree`
   - `explain_arm_gesture`
   - `explain_hand_left`
   - `explain_hand_right`
   - `idle_waiting`
4. Assign your desired animations to each hotkey

## Configuration

Add to your `.env` file:
```
VTS_ENABLED=true
VTS_HOST=localhost
VTS_PORT=8001
```

## Testing

Test the gestures by sending these messages:

1. **Wave Hello**: "Hello!" or "Hi there!" or "Assalamualaikum"
2. **Nod Agree**: "Yes" or "Correct" or "Betul"
3. **Explain Arm**: Ask "How do I apply to UiTM?" (AI will explain and trigger gesture)

## Troubleshooting

### Gestures not triggering
- Check VTS connection: `GET /vts/status`
- Verify hotkey IDs match exactly in VTube Studio
- Check browser console for error messages

### Toggle gesture stuck ON
- Call `disableExplainGesture()` or
- Manually trigger the hotkey again in VTube Studio

### Cooldown preventing gestures
- Default cooldown is 2 seconds between gestures
- Use `force: true` to bypass cooldown (not recommended for normal use)
