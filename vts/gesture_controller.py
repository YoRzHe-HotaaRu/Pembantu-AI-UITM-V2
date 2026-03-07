"""
Gesture Controller for VTube Studio
Manages head gestures and movements during speech to make the avatar more expressive.
Includes emphasis nods, head tilts, and rhythmic movement synced with speech.
"""

import asyncio
import random
import math
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
from enum import Enum


class EmotionType(Enum):
    """Emotion types for gesture mapping."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    THINKING = "thinking"
    SURPRISED = "surprised"
    CONFUSED = "confused"


@dataclass
class GestureConfig:
    """Configuration for gesture animations."""
    # Emphasis gesture settings
    emphasis_enabled: bool = True
    emphasis_nod_strength: float = 8.0  # Degrees for nod
    emphasis_tilt_strength: float = 5.0  # Degrees for tilt
    
    # Rhythmic movement settings
    rhythmic_enabled: bool = True
    rhythmic_amplitude: float = 3.0  # Degrees
    rhythmic_speed: float = 2.0  # Multiplier for speech rhythm
    
    # Engagement tracking
    engagement_enabled: bool = True
    engagement_range: float = 10.0  # Degrees
    
    # Emotion-based positions
    emotion_positions: Dict[EmotionType, Dict[str, float]] = None
    
    def __post_init__(self):
        if self.emotion_positions is None:
            self.emotion_positions = {
                EmotionType.NEUTRAL: {"x": 0, "y": 0, "z": 0},
                EmotionType.HAPPY: {"x": 0, "y": 5, "z": 0},
                EmotionType.SAD: {"x": 0, "y": -8, "z": 0},
                EmotionType.EXCITED: {"x": 0, "y": 3, "z": 5},
                EmotionType.THINKING: {"x": 0, "y": 2, "z": -8},
                EmotionType.SURPRISED: {"x": 0, "y": -5, "z": 0},
                EmotionType.CONFUSED: {"x": 5, "y": 3, "z": -5},
            }


class GestureController:
    """
    Manages expressive gestures during speech.
    Coordinates head movements with speech patterns and emotions.
    """
    
    # Punctuation that triggers gestures
    EMPHASIS_PUNCTUATION = ['!', '?', '.']
    PAUSE_PUNCTUATION = [',', ';', ':']
    
    def __init__(self, vts_connector, config: Optional[GestureConfig] = None):
        """
        Initialize the gesture controller.
        
        Args:
            vts_connector: VTSConnector instance
            config: GestureConfig instance (uses defaults if None)
        """
        self.vts = vts_connector
        self.config = config or GestureConfig()
        
        # State
        self._current_emotion = EmotionType.NEUTRAL
        self._is_speaking = False
        self._speech_start_time: float = 0
        self._current_text = ""
        
        # Animation state
        self._base_x = 0.0
        self._base_y = 0.0
        self._base_z = 0.0
        self._gesture_x = 0.0
        self._gesture_y = 0.0
        self._gesture_z = 0.0
        
        # Tasks
        self._gesture_task: Optional[asyncio.Task] = None
        self._rhythm_task: Optional[asyncio.Task] = None
        
    async def start_speaking(self, text: str = "", emotion: EmotionType = EmotionType.NEUTRAL):
        """
        Start speaking with gestures.
        
        Args:
            text: The text being spoken (for punctuation analysis)
            emotion: Current emotion for base positioning
        """
        self._is_speaking = True
        self._current_text = text
        self._speech_start_time = asyncio.get_event_loop().time()
        self._current_emotion = emotion
        
        # Set base position based on emotion
        emotion_pos = self.config.emotion_positions.get(emotion, {})
        self._base_x = emotion_pos.get("x", 0)
        self._base_y = emotion_pos.get("y", 0)
        self._base_z = emotion_pos.get("z", 0)
        
        # Start gesture tasks
        if self.config.emphasis_enabled:
            self._gesture_task = asyncio.create_task(self._emphasis_loop(text))
            
        if self.config.rhythmic_enabled:
            self._rhythm_task = asyncio.create_task(self._rhythm_loop())
            
        print(f"[GestureController] Started speaking with emotion: {emotion.value}")
        
    async def stop_speaking(self):
        """Stop speaking and reset gestures."""
        self._is_speaking = False
        
        # Cancel tasks
        if self._gesture_task:
            self._gesture_task.cancel()
            self._gesture_task = None
            
        if self._rhythm_task:
            self._rhythm_task.cancel()
            self._rhythm_task = None
            
        # Reset gesture offsets
        self._gesture_x = 0
        self._gesture_y = 0
        self._gesture_z = 0
        
        # Return to neutral
        await self._set_head_position(0, 0, 0)
        
        print("[GestureController] Stopped speaking")
        
    async def update_emotion(self, emotion: EmotionType):
        """Update emotion during speech."""
        self._current_emotion = emotion
        
        # Smoothly transition to new emotion position
        emotion_pos = self.config.emotion_positions.get(emotion, {})
        self._base_x = emotion_pos.get("x", 0)
        self._base_y = emotion_pos.get("y", 0)
        self._base_z = emotion_pos.get("z", 0)
        
    async def trigger_emphasis(self, strength: float = 1.0):
        """
        Trigger an emphasis gesture (nod).
        
        Args:
            strength: Gesture strength multiplier (0.0 - 2.0)
        """
        if not self._is_speaking:
            return
            
        # Quick downward nod
        original_y = self._gesture_y
        
        # Down
        self._gesture_y = -self.config.emphasis_nod_strength * strength
        await asyncio.sleep(0.1)
        
        # Up (slight overshoot)
        self._gesture_y = self.config.emphasis_nod_strength * strength * 0.3
        await asyncio.sleep(0.1)
        
        # Return
        self._gesture_y = original_y
        
    async def trigger_tilt(self, direction: str = "random", strength: float = 1.0):
        """
        Trigger a head tilt gesture.
        
        Args:
            direction: 'left', 'right', or 'random'
            strength: Gesture strength multiplier
        """
        if not self._is_speaking:
            return
            
        if direction == "random":
            direction = random.choice(["left", "right"])
            
        tilt_value = self.config.emphasis_tilt_strength * strength
        if direction == "right":
            tilt_value = -tilt_value
            
        original_z = self._gesture_z
        
        # Tilt
        self._gesture_z = tilt_value
        await asyncio.sleep(0.3)
        
        # Return
        self._gesture_z = original_z
        
    async def _emphasis_loop(self, text: str):
        """Analyze text and trigger emphasis gestures."""
        # Simple timing-based emphasis
        # In a real implementation, you'd sync with actual speech timing
        words = text.split()
        word_index = 0
        
        while self._is_speaking and word_index < len(words):
            word = words[word_index]
            
            # Check for emphasis punctuation
            if any(p in word for p in self.EMPHASIS_PUNCTUATION):
                await self.trigger_emphasis(strength=1.2)
                await asyncio.sleep(0.3)
            elif any(p in word for p in self.PAUSE_PUNCTUATION):
                await self.trigger_emphasis(strength=0.6)
                await asyncio.sleep(0.2)
            elif word_index % 5 == 0:  # Every 5th word, subtle emphasis
                await self.trigger_emphasis(strength=0.4)
                
            word_index += 1
            await asyncio.sleep(0.2)  # Approximate word timing
            
    async def _rhythm_loop(self):
        """Generate rhythmic head movement during speech."""
        while self._is_speaking:
            try:
                elapsed = asyncio.get_event_loop().time() - self._speech_start_time
                
                # Rhythmic bobbing
                rhythm_y = math.sin(elapsed * self.config.rhythmic_speed * 2 * math.pi) * \
                          self.config.rhythmic_amplitude
                
                # Add to gesture offset
                self._gesture_y = rhythm_y
                
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                break
                
    async def _set_head_position(self, x: float, y: float, z: float):
        """Send head position to VTube Studio."""
        if not self.vts or not self.vts.is_connected:
            return
            
        parameters = [
            {"id": "FaceAngleX", "value": x, "weight": 1.0},
            {"id": "FaceAngleY", "value": y, "weight": 1.0},
            {"id": "FaceAngleZ", "value": z, "weight": 1.0},
        ]
        
        try:
            await self.vts.set_parameters(parameters)
        except Exception as e:
            print(f"[GestureController] Error setting parameters: {e}")
            
    def get_current_position(self) -> Dict[str, float]:
        """Get current head position (base + gesture)."""
        return {
            "x": self._base_x + self._gesture_x,
            "y": self._base_y + self._gesture_y,
            "z": self._base_z + self._gesture_z,
        }
        
    async def update_loop(self):
        """Continuous update loop - call this regularly during speech."""
        while self._is_speaking:
            pos = self.get_current_position()
            await self._set_head_position(pos["x"], pos["y"], pos["z"])
            await asyncio.sleep(0.033)  # ~30fps


def detect_emotion_from_text(text: str) -> EmotionType:
    """
    Simple emotion detection from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Detected emotion type
    """
    text_lower = text.lower()
    
    # Happy indicators
    if any(word in text_lower for word in ['happy', 'glad', 'great', 'excellent', 'wonderful', 'terbaik', 'gembira', 'senang']):
        return EmotionType.HAPPY
        
    # Sad indicators
    if any(word in text_lower for word in ['sad', 'sorry', 'unfortunately', 'sedih', 'maaf']):
        return EmotionType.SAD
        
    # Excited indicators
    if any(word in text_lower for word in ['excited', 'amazing', 'awesome', 'wow', 'hebat', 'mantap']):
        return EmotionType.EXCITED
        
    # Surprised indicators
    if any(word in text_lower for word in ['surprised', 'shocked', 'wow', 'oh', 'terkejut']):
        return EmotionType.SURPRISED
        
    # Thinking indicators
    if any(word in text_lower for word in ['think', 'consider', 'perhaps', 'maybe', 'fikir', 'mungkin']):
        return EmotionType.THINKING
        
    # Confused indicators
    if any(word in text_lower for word in ['confused', 'unclear', 'what', 'huh', 'keliru']):
        return EmotionType.CONFUSED
        
    return EmotionType.NEUTRAL


# Global instance
_gesture_controller: Optional[GestureController] = None


def get_gesture_controller(vts_connector=None) -> GestureController:
    """Get or create the global gesture controller instance."""
    global _gesture_controller
    if _gesture_controller is None and vts_connector is not None:
        _gesture_controller = GestureController(vts_connector)
    return _gesture_controller
