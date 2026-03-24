"""
Main entry point for the Touchless Laptop Control System.

Orchestrates all components:
- Camera feed and gesture recognition
- Mouse/keyboard control
- Voice command processing
- Display and dashboard
"""

import cv2
import time
import threading
import sys
import os

import config
from gesture_control import GestureRecognizer
from mouse_controller import MouseController
from presentation_controller import PresentationController
from voice_control import VoiceController
from display import DisplayManager
from dashboard import Dashboard
from utils import CursorSmoother
from iris.eye_tracker import EyeMouseController


class TouchlessControlSystem:
    """
    Main system orchestrator for touchless laptop control.
    """

    def __init__(self):
        """Initialize all components."""
        print("[System] Initializing Touchless Control System...")

        # Controllers
        self.mouse_controller = MouseController()
        self.presentation_controller = PresentationController()
        self.gesture_recognizer = GestureRecognizer()
        self.display_manager = DisplayManager()
        self.cursor_smoother = CursorSmoother(
            smoothing_factor=config.SMOOTHING_FACTOR,
            dead_zone=config.DEAD_ZONE_RADIUS
        )

        # Voice control (initialized but not started)
        self.voice_controller = VoiceController(
            self.mouse_controller,
            self.presentation_controller
        )

        # State
        self.running = False
        self.voice_enabled = False
        self.control_mode = "hand"
        self.camera = None
        self.iris_controller = None

        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()

        print("[System] Initialization complete")

    def start(self, mode="hand"):
        """Start the control system."""
        if self.running:
            print("[System] Already running")
            return

        self.control_mode = mode
        print(f"[System] Starting in {self.control_mode} mode...")
        self.running = True

        if self.control_mode == "iris":
            iris_config = os.path.join(os.path.dirname(__file__), "iris", "config.yaml")
            self.iris_controller = EyeMouseController(config_path=iris_config)
            self.thread = threading.Thread(target=self._iris_main_loop, daemon=True)
            self.thread.start()
            print("[System] Iris mode started successfully")
            return

        # Open camera
        self.camera = cv2.VideoCapture(config.CAMERA_INDEX)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.camera.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)

        if not self.camera.isOpened():
            print("[System] ERROR: Could not open camera")
            self.running = False
            return

        # Setup display
        self.display_manager.setup_window()

        # Run main loop in separate thread
        self.thread = threading.Thread(target=self._hand_main_loop, daemon=True)
        self.thread.start()

        print("[System] Hand mode started successfully")

    def stop(self):
        """Stop the control system."""
        if not self.running:
            return

        print("[System] Stopping...")
        self.running = False

        # Stop iris mode loop
        if self.iris_controller:
            self.iris_controller.stop()

        # Wait for thread to finish
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2)

        # Stop voice control
        if self.voice_enabled:
            self.voice_controller.stop_listening()

        # Release resources
        if self.camera:
            self.camera.release()
            self.camera = None
        self.iris_controller = None
        self.gesture_recognizer.close()
        self.display_manager.close()

        print("[System] Stopped")

    def toggle_voice_control(self, enabled):
        """
        Enable or disable voice control.

        Args:
            enabled: bool, True to enable voice control
        """
        self.voice_enabled = enabled
        if enabled:
            self.voice_controller.start_listening()
        else:
            self.voice_controller.stop_listening()

    def _hand_main_loop(self):
        """Hand-gesture processing loop (runs in separate thread)."""
        last_gesture = config.GESTURE_NONE

        while self.running:
            # Read frame
            ret, frame = self.camera.read()
            if not ret:
                print("[System] Failed to read frame")
                break

            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)

            # Process frame with MediaPipe
            results, rgb_frame = self.gesture_recognizer.process_frame(frame)

            gesture = config.GESTURE_NONE

            # If hand detected
            if results and results.hand_landmarks:
                for hand_landmarks in results.hand_landmarks:
                    # Draw landmarks
                    frame = self.gesture_recognizer.draw_landmarks(frame, results)

                    # Recognize gesture
                    # MediaPipe Tasks API returns hand_landmarks directly as list of landmarks
                    landmarks = hand_landmarks
                    gesture = self.gesture_recognizer.recognize_gesture(landmarks)

                    # Get cursor position
                    raw_x, raw_y = self.gesture_recognizer.get_cursor_position(
                        landmarks,
                        config.CAMERA_WIDTH,
                        config.CAMERA_HEIGHT
                    )

                    # Smooth cursor position
                    smooth_x, smooth_y = self.cursor_smoother.smooth(raw_x, raw_y)

                    # Execute actions based on gesture
                    self._execute_gesture_action(gesture, smooth_x, smooth_y, last_gesture)

                    last_gesture = gesture
                    break  # Only process first hand

            # Update cooldown
            self.gesture_recognizer.update_cooldown()

            # Get voice command
            voice_command = self.voice_controller.get_last_command() if self.voice_enabled else ""

            # Calculate FPS
            self.frame_count += 1
            elapsed = time.time() - self.fps_start_time
            if elapsed >= 1.0:
                self.fps = self.frame_count / elapsed
                self.frame_count = 0
                self.fps_start_time = time.time()

            # Draw overlay
            frame = self.display_manager.draw_overlay(frame, gesture, voice_command, self.fps)

            # Display frame
            self.display_manager.show_frame(frame)

            # Check for quit key
            key = self.display_manager.wait_key(1)
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("[System] Quit key pressed")
                self.running = False
                break

    def _iris_main_loop(self):
        """Iris eye-tracking loop (runs in separate thread)."""
        try:
            if self.iris_controller:
                self.iris_controller.run()
        finally:
            self.running = False

    def _execute_gesture_action(self, gesture, x, y, last_gesture):
        """
        Execute action based on detected gesture.

        Args:
            gesture: str, detected gesture
            x: int, cursor x-coordinate
            y: int, cursor y-coordinate
            last_gesture: str, previous gesture
        """
        # Skip if on cooldown
        if self.gesture_recognizer.is_on_cooldown():
            return

        if gesture == config.GESTURE_MOVE:
            self.mouse_controller.move_cursor(x, y)

        elif gesture == config.GESTURE_LEFT_CLICK:
            if last_gesture != config.GESTURE_LEFT_CLICK:
                self.mouse_controller.left_click()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Left click")

        elif gesture == config.GESTURE_RIGHT_CLICK:
            if last_gesture != config.GESTURE_RIGHT_CLICK:
                self.mouse_controller.right_click()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Right click")

        elif gesture == config.GESTURE_DRAG:
            self.mouse_controller.start_drag()
            self.mouse_controller.move_cursor(x, y)
            print("[Gesture] Dragging")

        elif gesture == config.GESTURE_SCROLL_UP:
            self.mouse_controller.scroll_up()
            self.gesture_recognizer.trigger_cooldown()
            print("[Gesture] Scroll up")

        elif gesture == config.GESTURE_SCROLL_DOWN:
            self.mouse_controller.scroll_down()
            self.gesture_recognizer.trigger_cooldown()
            print("[Gesture] Scroll down")

        elif gesture == config.GESTURE_NEXT_SLIDE:
            if last_gesture != config.GESTURE_NEXT_SLIDE:
                self.presentation_controller.next_slide()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Next slide")

        elif gesture == config.GESTURE_PREV_SLIDE:
            if last_gesture != config.GESTURE_PREV_SLIDE:
                self.presentation_controller.previous_slide()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Previous slide")

        # End drag if not dragging anymore
        if last_gesture == config.GESTURE_DRAG and gesture != config.GESTURE_DRAG:
            self.mouse_controller.end_drag()
            print("[Gesture] Released drag")


def main():
    """Main function."""
    print("="*60)
    print("  TOUCHLESS LAPTOP CONTROL SYSTEM")
    print("  Using Hand Gestures and Voice Commands")
    print("="*60)
    print()

    # Create system
    system = TouchlessControlSystem()

    # Create dashboard
    dashboard = Dashboard(
        start_callback=system.start,
        stop_callback=system.stop,
        voice_toggle_callback=system.toggle_voice_control
    )

    print("[Main] Dashboard launched")
    print("[Main] Click 'Start System' to begin")
    print()

    try:
        # Run dashboard (blocking)
        dashboard.run()
    except KeyboardInterrupt:
        print("\n[Main] Interrupted by user")
    finally:
        # Cleanup
        system.stop()
        dashboard.close()
        print("[Main] Goodbye!")


if __name__ == "__main__":
    main()
