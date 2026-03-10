"""
Gesture Animator for VTube Studio
Manages hotkey-based gesture animations triggered by user input and AI responses.
Includes wave, nod, explanation gestures, and idle variations.
"""

import asyncio
import time
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from enum import Enum


class GestureType(Enum):
    """Types of gestures supported."""
    WAVE_HELLO = "wave_hello"
    NOD_AGREE = "nod_head_agree"
    EXPLAIN_ARM = "explain_arm_gesture"
    EXPLAIN_LEFT = "explain_hand_left"
    EXPLAIN_RIGHT = "explain_hand_right"
    IDLE_WAITING = "idle_waiting"


class GestureCategory(Enum):
    """Categories for gesture triggering."""
    GREETING = "greeting"
    AGREEMENT = "agreement"
    EXPLANATION = "explanation"
    IDLE = "idle"


@dataclass
class GestureConfig:
    """Configuration for gesture animations."""
    # Cooldown between gestures (seconds)
    gesture_cooldown: float = 2.0
    
    # Toggle gestures (these need to be triggered twice to turn off)
    toggle_gestures: List[GestureType] = field(default_factory=lambda: [GestureType.EXPLAIN_ARM])
    
    # Auto-disable toggle gestures after response (seconds)
    toggle_auto_disable_delay: float = 0.5
    
    # Greeting keywords (English and Malay)
    greeting_keywords: List[str] = field(default_factory=lambda: [
        # English
        "hello", "hi", "hey", "greetings", "welcome", "good morning", "good afternoon",
        "good evening", "howdy", "yo", "what's up", "sup",
        # Malay
        "assalamualaikum", "salam", "helo", "hai", "selamat pagi", "selamat petang",
        "selamat malam", "apa khabar", "apakhabar"
    ])
    
    # Agreement keywords
    agreement_keywords: List[str] = field(default_factory=lambda: [
        # English
        "yes", "yeah", "yep", "correct", "right", "exactly", "absolutely", "sure",
        "definitely", "indeed", "agreed", "ok", "okay", "alright", "true",
        # Malay
        "ya", "betul", "benar", "setuju", "baik", "ok", "boleh", "mestilah"
    ])
    
    # Explanation indicators (for AI responses)
    explanation_indicators: List[str] = field(default_factory=lambda: [
        # English
        "here's how", "let me explain", "to explain", "this means", "in other words",
        "basically", "essentially", "the reason", "because", "therefore", "this is why",
        "what this means", "how it works", "the process", "steps to", "procedure",
        # Malay
        "begini", "mari saya terangkan", "untuk menerangkan", "ini bermaksud",
        "secara ringkas", "sebabnya", "kerana", "oleh itu", "inilah sebabnya",
        "cara kerja", "proses", "langkah-langkah", "tata cara"
    ])


class GestureAnimator:
    """
    Manages gesture animations via VTube Studio hotkeys.
    Coordinates with idle animator and handles toggle states.
    """
    
    def __init__(self, vts_connector, config: Optional[GestureConfig] = None):
        """
        Initialize the gesture animator.
        
        Args:
            vts_connector: VTSConnector instance
            config: GestureConfig instance (uses defaults if None)
        """
        self.vts = vts_connector
        self.config = config or GestureConfig()
        
        # State tracking
        self._last_gesture_time: float = 0
        self._active_toggles: Dict[GestureType, bool] = {}
        self._gesture_queue: List[GestureType] = []
        self._is_processing: bool = False
        
        # Gesture to hotkey mapping
        self._gesture_hotkeys: Dict[GestureType, str] = {
            GestureType.WAVE_HELLO: "wave_hello",
            GestureType.NOD_AGREE: "nod_head_agree",
            GestureType.EXPLAIN_ARM: "explain_arm_gesture",
            GestureType.EXPLAIN_LEFT: "explain_hand_left",
            GestureType.EXPLAIN_RIGHT: "explain_hand_right",
            GestureType.IDLE_WAITING: "idle_waiting",
        }
        
        # Callbacks
        self._on_gesture_triggered: Optional[Callable[[GestureType], None]] = None
        
    async def trigger_gesture(self, gesture: GestureType, force: bool = False) -> bool:
        """
        Trigger a gesture animation.
        
        Args:
            gesture: The gesture type to trigger
            force: If True, bypass cooldown check
            
        Returns:
            True if gesture was triggered
        """
        if not self.vts or not self.vts.is_connected:
            print(f"[GestureAnimator] Cannot trigger {gesture.value} - VTS not connected")
            return False
        
        # Check cooldown
        current_time = time.time()
        if not force and (current_time - self._last_gesture_time) < self.config.gesture_cooldown:
            remaining = self.config.gesture_cooldown - (current_time - self._last_gesture_time)
            print(f"[GestureAnimator] Gesture on cooldown ({remaining:.1f}s remaining)")
            return False
        
        # Handle toggle gestures
        if gesture in self.config.toggle_gestures:
            return await self._handle_toggle_gesture(gesture)
        
        # Trigger the hotkey
        return await self._trigger_hotkey(gesture)
        
    async def _handle_toggle_gesture(self, gesture: GestureType) -> bool:
        """Handle toggle-type gestures (on/off)."""
        is_active = self._active_toggles.get(gesture, False)
        hotkey = self._gesture_hotkeys.get(gesture)
        
        if not hotkey:
            return False
        
        try:
            # Toggle the gesture
            success = await self.vts.trigger_hotkey(hotkey)
            
            if success:
                # Toggle the state
                self._active_toggles[gesture] = not is_active
                new_state = "ON" if self._active_toggles[gesture] else "OFF"
                print(f"[GestureAnimator] Toggle gesture {gesture.value}: {new_state}")
                self._last_gesture_time = time.time()
                
                if self._on_gesture_triggered:
                    self._on_gesture_triggered(gesture)
                    
            return success
            
        except Exception as e:
            print(f"[GestureAnimator] Error triggering toggle gesture {gesture.value}: {e}")
            return False
    
    async def _trigger_hotkey(self, gesture: GestureType) -> bool:
        """Trigger a hotkey for a gesture."""
        hotkey = self._gesture_hotkeys.get(gesture)
        
        if not hotkey:
            print(f"[GestureAnimator] No hotkey mapped for {gesture.value}")
            return False
        
        try:
            success = await self.vts.trigger_hotkey(hotkey)
            
            if success:
                print(f"[GestureAnimator] Triggered gesture: {gesture.value}")
                self._last_gesture_time = time.time()
                
                if self._on_gesture_triggered:
                    self._on_gesture_triggered(gesture)
            else:
                print(f"[GestureAnimator] Failed to trigger gesture: {gesture.value}")
                
            return success
            
        except Exception as e:
            print(f"[GestureAnimator] Error triggering gesture {gesture.value}: {e}")
            return False
    
    async def disable_toggle(self, gesture: GestureType) -> bool:
        """
        Disable a toggle gesture if it's currently active.
        
        Args:
            gesture: The toggle gesture to disable
            
        Returns:
            True if gesture was disabled
        """
        if gesture not in self.config.toggle_gestures:
            return False
            
        if not self._active_toggles.get(gesture, False):
            return True  # Already off
            
        # Trigger again to turn off
        return await self._handle_toggle_gesture(gesture)
    
    async def disable_all_toggles(self):
        """Disable all active toggle gestures."""
        for gesture in self.config.toggle_gestures:
            if self._active_toggles.get(gesture, False):
                await self.disable_toggle(gesture)
                await asyncio.sleep(0.1)  # Small delay between toggles
    
    def detect_greeting(self, text: str) -> bool:
        """
        Detect if text contains a greeting.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if greeting detected
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.config.greeting_keywords)
    
    def detect_agreement(self, text: str) -> bool:
        """
        Detect if text indicates agreement/confirmation.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if agreement detected
        """
        text_lower = text.lower()
        # Check for standalone agreement words or short confirmations
        words = text_lower.split()
        return any(keyword in text_lower for keyword in self.config.agreement_keywords) or \
               (len(words) <= 3 and any(word in self.config.agreement_keywords for word in words))
    
    def detect_explanation_context(self, text: str) -> bool:
        """
        Detect if text is explaining something.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if explanation context detected
        """
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in self.config.explanation_indicators)
    
    async def auto_trigger_from_user_input(self, text: str) -> Optional[GestureType]:
        """
        Automatically detect and trigger appropriate gesture from user input.
        
        Args:
            text: User input text
            
        Returns:
            Triggered gesture type or None
        """
        # Priority: Greeting > Agreement
        if self.detect_greeting(text):
            success = await self.trigger_gesture(GestureType.WAVE_HELLO)
            return GestureType.WAVE_HELLO if success else None
            
        if self.detect_agreement(text):
            success = await self.trigger_gesture(GestureType.NOD_AGREE)
            return GestureType.NOD_AGREE if success else None
            
        return None
    
    async def auto_trigger_from_ai_response(self, text: str) -> Optional[GestureType]:
        """
        Automatically detect and trigger appropriate gesture from AI response.
        
        Args:
            text: AI response text
            
        Returns:
            Triggered gesture type or None
        """
        if self.detect_explanation_context(text):
            # For explanations, use the arm gesture (toggle on)
            success = await self.trigger_gesture(GestureType.EXPLAIN_ARM)
            return GestureType.EXPLAIN_ARM if success else None
            
        return None
    
    def get_active_toggles(self) -> List[GestureType]:
        """Get list of currently active toggle gestures."""
        return [g for g, active in self._active_toggles.items() if active]
    
    def is_toggle_active(self, gesture: GestureType) -> bool:
        """Check if a toggle gesture is currently active."""
        return self._active_toggles.get(gesture, False)
    
    def set_gesture_callback(self, callback: Callable[[GestureType], None]):
        """Set callback for when gestures are triggered."""
        self._on_gesture_triggered = callback
    
    async def trigger_random_idle(self) -> bool:
        """Trigger a random idle animation change."""
        return await self.trigger_gesture(GestureType.IDLE_WAITING)


# Global instance
_gesture_animator: Optional[GestureAnimator] = None


def get_gesture_animator(vts_connector=None) -> GestureAnimator:
    """Get or create the global gesture animator instance."""
    global _gesture_animator
    if _gesture_animator is None and vts_connector is not None:
        _gesture_animator = GestureAnimator(vts_connector)
    return _gesture_animator


def detect_user_intent(text: str) -> Dict[str, bool]:
    """
    Detect various intents from user text.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of detected intents
    """
    config = GestureConfig()
    text_lower = text.lower()
    
    return {
        "is_greeting": any(kw in text_lower for kw in config.greeting_keywords),
        "is_agreement": any(kw in text_lower for kw in config.agreement_keywords),
        "is_explanation": any(ind in text_lower for ind in config.explanation_indicators),
    }
