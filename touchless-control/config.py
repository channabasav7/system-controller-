"""
Configuration constants for the Touchless Laptop Control System.

This module centralizes all tunable parameters including camera settings,
gesture thresholds, cursor smoothing factors, and voice command mappings.
"""

import pyautogui

# ──────────────────────────── Screen & Camera ────────────────────────────
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ──────────────────────────── MediaPipe Hands ────────────────────────────
MP_MAX_HANDS = 1
MP_DETECTION_CONFIDENCE = 0.7
MP_TRACKING_CONFIDENCE = 0.7

# ──────────────────────────── Gesture Thresholds ─────────────────────────
# Distance (normalised) between two landmarks to count as a "touch"
TOUCH_THRESHOLD = 0.045

# Minimum vertical movement (normalised) to register a scroll gesture
SCROLL_MOVE_THRESHOLD = 0.03

# Number of consecutive frames a gesture must be held to trigger an action
GESTURE_HOLD_FRAMES = 3

# Cooldown (in frames) after a click / slide action to avoid repeats
ACTION_COOLDOWN_FRAMES = 15

# ──────────────────────────── Cursor Smoothing ───────────────────────────
# Exponential moving‑average factor (0 = max smooth, 1 = no smoothing)
SMOOTHING_FACTOR = 0.4

# Dead‑zone radius in pixels — movements smaller than this are ignored
DEAD_ZONE_RADIUS = 5

# ──────────────────────────── Drag & Drop ────────────────────────────────
DRAG_START_FRAMES = 5  # frames of pinch before drag mode activates

# ──────────────────────────── Scroll ─────────────────────────────────────
SCROLL_SPEED = 5  # lines per scroll tick

# ──────────────────────────── Voice Recognition ──────────────────────────
VOICE_ENERGY_THRESHOLD = 300
VOICE_PAUSE_THRESHOLD = 0.8  # seconds of silence to end a phrase
VOICE_TIMEOUT = 5  # seconds to wait for speech before giving up

# Mapping of spoken phrases → internal command names
VOICE_COMMANDS = {
    "open chrome":          "open_chrome",
    "open powerpoint":      "open_powerpoint",
    "open power point":     "open_powerpoint",
    "next slide":           "next_slide",
    "next":                 "next_slide",
    "previous slide":       "previous_slide",
    "previous":             "previous_slide",
    "scroll down":          "scroll_down",
    "scroll up":            "scroll_up",
    "close window":         "close_window",
    "start presentation":   "start_presentation",
    "stop presentation":    "stop_presentation",
    "minimize":             "minimize_window",
    "maximize":             "maximize_window",
    "open notepad":         "open_notepad",
    "open calculator":      "open_calculator",
    "take screenshot":      "take_screenshot",
}

# ──────────────────────────── Gesture Names ──────────────────────────────
GESTURE_NONE = "None"
GESTURE_MOVE = "Move Cursor"
GESTURE_LEFT_CLICK = "Left Click"
GESTURE_RIGHT_CLICK = "Right Click"
GESTURE_DRAG = "Drag & Drop"
GESTURE_SCROLL_UP = "Scroll Up"
GESTURE_SCROLL_DOWN = "Scroll Down"
GESTURE_NEXT_SLIDE = "Next Slide"
GESTURE_PREV_SLIDE = "Previous Slide"
GESTURE_LASER = "Laser Pointer"

# ──────────────────────────── Display / Overlay ──────────────────────────
OVERLAY_FONT_SCALE = 0.6
OVERLAY_THICKNESS = 2
OVERLAY_COLOR_GESTURE = (0, 255, 0)    # green
OVERLAY_COLOR_VOICE = (255, 200, 0)    # cyan‑ish
OVERLAY_COLOR_LANDMARK = (0, 255, 255) # yellow
OVERLAY_COLOR_LASER = (0, 0, 255)      # red

# ──────────────────────────── Dashboard ──────────────────────────────────
DASHBOARD_WIDTH = 420
DASHBOARD_HEIGHT = 520
