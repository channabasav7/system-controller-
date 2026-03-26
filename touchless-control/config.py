"""
Configuration constants for the Touchless Laptop Control System.

This module centralizes all tunable parameters including camera settings,
gesture thresholds, cursor smoothing factors, and voice command mappings.
"""

import pyautogui

# ──────────────────────────── Screen & Camera ────────────────────────────
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
CAMERA_INDEX = 0
CAMERA_INDICES = [0, 1, 2]
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
CAMERA_READ_RETRY_LIMIT = 30

# ──────────────────────────── MediaPipe Hands ────────────────────────────
MP_MAX_HANDS = 2
MP_DETECTION_CONFIDENCE = 0.45
MP_TRACKING_CONFIDENCE = 0.45

# ──────────────────────────── Gesture Thresholds ─────────────────────────
# Distance (normalised) between two landmarks to count as a "touch"
TOUCH_THRESHOLD = 0.045

# Minimum distance between fingers for peace sign / slide gestures
PEACE_THRESHOLD = 0.08

# Minimum vertical movement (normalised) to register a scroll gesture
SCROLL_MOVE_THRESHOLD = 0.03
SWIPE_THRESHOLD = 0.12
SWIPE_HISTORY_FRAMES = 6

# Number of consecutive frames a gesture must be held to trigger an action
GESTURE_HOLD_FRAMES = 3

# Cooldown (in frames) after a click / slide action to avoid repeats
ACTION_COOLDOWN_FRAMES = 15

# ──────────────────────────── Cursor Smoothing ───────────────────────────
# Exponential moving‑average factor (0 = max smooth, 1 = no smoothing)
SMOOTHING_FACTOR = 0.25

# Dead‑zone radius in pixels — movements smaller than this are ignored
DEAD_ZONE_RADIUS = 3

# Adaptive smoothing: fast motion uses higher alpha, slow motion uses lower alpha.
SMOOTHING_ALPHA_MIN = 0.18
SMOOTHING_ALPHA_MAX = 0.55
SMOOTHING_VELOCITY_SCALE = 120.0

# Hand active region margins for cursor mapping (0.0 to 0.5)
CURSOR_ACTIVE_MARGIN_X = 0.08
CURSOR_ACTIVE_MARGIN_Y = 0.08

# Weighted blend for index tip + MCP for stable but precise pointing.
CURSOR_TIP_WEIGHT = 0.7

# ──────────────────────────── Drag & Drop ────────────────────────────────
DRAG_START_FRAMES = 5  # frames of pinch before drag mode activates

# ──────────────────────────── Two-Hand Gestures ─────────────────────────
TWO_HAND_SPREAD_THRESHOLD = 0.35
TWO_HAND_CLOSE_THRESHOLD = 0.18

# ──────────────────────────── Scroll ─────────────────────────────────────
SCROLL_SPEED = 5  # lines per scroll tick

# ──────────────────────────── Voice Recognition ──────────────────────────
VOICE_ENERGY_THRESHOLD = 300
VOICE_PAUSE_THRESHOLD = 0.8  # seconds of silence to end a phrase
VOICE_TIMEOUT = 5  # seconds to wait for speech before giving up

# Mapping of spoken phrases → internal command names
VOICE_COMMANDS = {
    "open chrome":          "open_chrome",
    "open browser":         "open_chrome",
    "open powerpoint":      "open_powerpoint",
    "open power point":     "open_powerpoint",
    "next slide":           "next_slide",
    "next":                 "next_slide",
    "previous slide":       "previous_slide",
    "previous":             "previous_slide",
    "go to slide":          "go_to_slide",
    "black screen":         "black_screen",
    "scroll down":          "scroll_down",
    "scroll up":            "scroll_up",
    "zoom in":              "zoom_in",
    "zoom out":             "zoom_out",
    "close window":         "close_window",
    "start presentation":   "start_presentation",
    "stop presentation":    "stop_presentation",
    "end presentation":     "stop_presentation",
    "minimize":             "minimize_window",
    "maximize":             "maximize_window",
    "open notepad":         "open_notepad",
    "open calculator":      "open_calculator",
    "take screenshot":      "take_screenshot",
    "volume up":            "volume_up",
    "volume down":          "volume_down",
    "mute":                 "mute_audio",
    "lock screen":          "lock_screen",
    "switch window":        "switch_window",
    "open task manager":    "open_task_manager",
    "copy":                 "copy",
    "paste":                "paste",
    "select all":           "select_all",
    "undo":                 "undo",
    "redo":                 "redo",
    "bold":                 "bold",
    "italic":               "italic",
    "underline":            "underline",
    "align left":           "align_left",
    "center":               "center_align",
    "save document":        "save_document",
    "new paragraph":        "new_paragraph",
    "start dictation":      "start_dictation",
    "stop dictation":       "stop_dictation",
    "presentation mode":    "set_profile_presentation",
    "browser mode":         "set_profile_browser",
    "writing mode":         "set_profile_writing",
    "default mode":         "set_profile_default",
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
GESTURE_VOLUME_UP = "Volume Up"
GESTURE_VOLUME_DOWN = "Volume Down"
GESTURE_SWIPE_LEFT = "Swipe Left"
GESTURE_SWIPE_RIGHT = "Swipe Right"
GESTURE_SWIPE_UP = "Swipe Up"
GESTURE_SWIPE_DOWN = "Swipe Down"
GESTURE_TWO_HAND_LOCK = "Two-Hand Lock Screen"
GESTURE_TWO_HAND_ZOOM_IN = "Two-Hand Zoom In"
GESTURE_TWO_HAND_ZOOM_OUT = "Two-Hand Zoom Out"
GESTURE_TWO_HAND_COPY = "Two-Hand Copy"
GESTURE_TWO_HAND_PASTE = "Two-Hand Paste"

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
