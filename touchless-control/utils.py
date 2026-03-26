"""
Utility functions for gesture recognition and cursor control.

Includes:
- Euclidean distance calculation
- Finger state detection (up/down) based on landmarks
- Exponential moving average for cursor smoothing
- Dead‑zone filtering
"""

import math
import numpy as np


def euclidean_distance(p1, p2):
    """
    Compute Euclidean distance between two 2D points.

    Args:
        p1: tuple (x, y)
        p2: tuple (x, y)

    Returns:
        float: distance
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def get_fingers_up(landmarks):
    """
    Determine which fingers are extended (up).

    MediaPipe Hands landmark indices:
      0: WRIST
      1–4: THUMB (CMC, MCP, IP, TIP)
      5–8: INDEX (MCP, PIP, DIP, TIP)
      9–12: MIDDLE (MCP, PIP, DIP, TIP)
      13–16: RING (MCP, PIP, DIP, TIP)
      17–20: PINKY (MCP, PIP, DIP, TIP)

    Args:
        landmarks: list of 21 normalized hand landmarks from MediaPipe
                   Each landmark has .x, .y, .z attributes

    Returns:
        list[bool]: [thumb_up, index_up, middle_up, ring_up, pinky_up]
    """
    fingers_state = []

    # ────────────── Thumb (compare x‑coordinate for horizontal detection) ───────
    # For right hand: thumb tip (4) should be to the left of IP (3)
    # For left hand: thumb tip should be to the right of IP
    # Simple heuristic: use wrist (0) to determine handedness
    if landmarks[4].x < landmarks[3].x:
        # Likely right hand
        fingers_state.append(landmarks[4].x < landmarks[3].x)
    else:
        # Likely left hand
        fingers_state.append(landmarks[4].x > landmarks[3].x)

    # ────────────── Other fingers (compare y‑coordinate) ────────────────────────
    # Finger is "up" if TIP is above PIP (lower y = higher on screen)
    tip_indices = [8, 12, 16, 20]      # INDEX, MIDDLE, RING, PINKY tips
    pip_indices = [6, 10, 14, 18]      # corresponding PIP joints

    for tip_idx, pip_idx in zip(tip_indices, pip_indices):
        fingers_state.append(landmarks[tip_idx].y < landmarks[pip_idx].y)

    return fingers_state


def count_fingers(fingers_up):
    """
    Count how many fingers are extended.

    Args:
        fingers_up: list[bool] from get_fingers_up()

    Returns:
        int: number of fingers currently extended
    """
    return sum(fingers_up)


class CursorSmoother:
    """
    Applies exponential moving average to smooth cursor position.
    Also enforces a dead‑zone to ignore tiny jitters.
    """

    def __init__(self, smoothing_factor=0.4, dead_zone=5):
        """
        Args:
            smoothing_factor: float in [0,1]. Higher = less smoothing.
            dead_zone: int, radius in pixels within which movement is ignored.
        """
        self.alpha = smoothing_factor
        self.dead_zone = dead_zone
        self.prev_x = None
        self.prev_y = None

        # Adaptive smoothing bounds and motion scaling.
        self.alpha_min = 0.18
        self.alpha_max = 0.55
        self.velocity_scale = 120.0

    def configure_adaptive(self, alpha_min=0.18, alpha_max=0.55, velocity_scale=120.0):
        """Configure adaptive smoothing parameters."""
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.velocity_scale = max(1.0, velocity_scale)

    def smooth(self, raw_x, raw_y):
        """
        Smooth the raw coordinates using exponential moving average.

        Args:
            raw_x: int, new x‑coordinate
            raw_y: int, new y‑coordinate

        Returns:
            (smooth_x, smooth_y): tuple of smoothed coordinates
        """
        if self.prev_x is None:
            # First call — initialise
            self.prev_x = raw_x
            self.prev_y = raw_y
            return raw_x, raw_y

        # Adaptive alpha: move faster when far away, smoother when near target.
        delta_x = raw_x - self.prev_x
        delta_y = raw_y - self.prev_y
        velocity = math.sqrt(delta_x**2 + delta_y**2)
        v_norm = min(1.0, velocity / self.velocity_scale)
        alpha = self.alpha_min + (self.alpha_max - self.alpha_min) * v_norm

        # Exponential moving average with adaptive alpha.
        smooth_x = alpha * raw_x + (1 - alpha) * self.prev_x
        smooth_y = alpha * raw_y + (1 - alpha) * self.prev_y

        # Apply dead‑zone
        dist = math.sqrt((smooth_x - self.prev_x)**2 + (smooth_y - self.prev_y)**2)
        if dist < self.dead_zone:
            # Too small, ignore
            return int(self.prev_x), int(self.prev_y)

        self.prev_x = smooth_x
        self.prev_y = smooth_y
        return int(smooth_x), int(smooth_y)

    def reset(self):
        """Reset the smoother state."""
        self.prev_x = None
        self.prev_y = None


def normalize_landmarks(landmarks, width, height):
    """
    Convert normalized landmarks (0–1 range) to pixel coordinates.

    Args:
        landmarks: list of MediaPipe landmarks with .x, .y attributes
        width: int, frame width
        height: int, frame height

    Returns:
        list of tuples [(x, y), ...] in pixel coordinates
    """
    return [(int(lm.x * width), int(lm.y * height)) for lm in landmarks]
