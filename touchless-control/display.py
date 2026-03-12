"""
Display module for real‑time video overlay.

Renders the camera feed with hand landmarks, detected gestures,
and voice commands overlaid on the frame.
"""

import cv2
import config


class DisplayManager:
    """
    Manages the video display window and overlay rendering.
    """

    def __init__(self):
        """Initialize display manager."""
        self.window_name = "Touchless Laptop Control"

    def setup_window(self):
        """Create and configure the display window."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, config.CAMERA_WIDTH, config.CAMERA_HEIGHT)

    def draw_overlay(self, frame, gesture, voice_command, fps=0):
        """
        Draw overlay information on the frame.

        Args:
            frame: BGR image from OpenCV
            gesture: str, current detected gesture
            voice_command: str, last voice command
            fps: float, current FPS

        Returns:
            frame with overlay drawn
        """
        height, width, _ = frame.shape

        # ────────────── Top bar background ──────────────────────────────────
        cv2.rectangle(frame, (0, 0), (width, 80), (40, 40, 40), -1)

        # ────────────── Gesture status ──────────────────────────────────────
        gesture_text = f"Gesture: {gesture}"
        cv2.putText(
            frame,
            gesture_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            config.OVERLAY_FONT_SCALE,
            config.OVERLAY_COLOR_GESTURE,
            config.OVERLAY_THICKNESS
        )

        # ────────────── Voice command status ────────────────────────────────
        if voice_command:
            voice_text = f"Voice: {voice_command}"
            cv2.putText(
                frame,
                voice_text,
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                config.OVERLAY_FONT_SCALE,
                config.OVERLAY_COLOR_VOICE,
                config.OVERLAY_THICKNESS
            )

        # ────────────── FPS counter ─────────────────────────────────────────
        if fps > 0:
            fps_text = f"FPS: {int(fps)}"
            cv2.putText(
                frame,
                fps_text,
                (width - 100, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                config.OVERLAY_FONT_SCALE,
                (255, 255, 255),
                config.OVERLAY_THICKNESS
            )

        # ────────────── Instructions ────────────────────────────────────────
        instructions = [
            "1 finger = Move",
            "Index+Thumb = Click",
            "2 fingers = Scroll",
            "3 fingers = Slides",
            "Press 'q' to quit"
        ]

        y_offset = height - 120
        for instruction in instructions:
            cv2.putText(
                frame,
                instruction,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1
            )
            y_offset += 20

        return frame

    def show_frame(self, frame):
        """
        Display the frame in the window.

        Args:
            frame: BGR image to display
        """
        cv2.imshow(self.window_name, frame)

    def wait_key(self, delay=1):
        """
        Wait for a key press.

        Args:
            delay: int, milliseconds to wait

        Returns:
            int: key code of pressed key, or -1 if no key pressed
        """
        return cv2.waitKey(delay)

    def close(self):
        """Close all OpenCV windows."""
        cv2.destroyAllWindows()
