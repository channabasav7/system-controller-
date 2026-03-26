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
from profile_manager import ProfileManager


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
        self.profile_manager = ProfileManager()
        self.cursor_smoother = CursorSmoother(
            smoothing_factor=config.SMOOTHING_FACTOR,
            dead_zone=config.DEAD_ZONE_RADIUS
        )

        # Voice control (initialized but not started)
        self.voice_controller = VoiceController(
            self.mouse_controller,
            self.presentation_controller,
            profile_manager=self.profile_manager
        )

        # State
        self.running = False
        self.voice_enabled = False
        self.control_mode = "hand"
        self.camera = None
        self.iris_controller = None
        self.latest_display_frame = None
        self.frame_lock = threading.Lock()

        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.active_profile = "default"
        self.last_profile_update_time = 0

        print("[System] Initialization complete")

    def _open_camera(self):
        """Open camera with backend fallbacks for better Windows stability."""
        backends = [
            ("DirectShow", cv2.CAP_DSHOW),
            ("Default", None),
        ]
        camera_indices = getattr(config, "CAMERA_INDICES", [config.CAMERA_INDEX])

        for index in camera_indices:
            for backend_name, backend in backends:
                try:
                    if backend is None:
                        camera = cv2.VideoCapture(index)
                    else:
                        camera = cv2.VideoCapture(index, backend)

                    if not camera or not camera.isOpened():
                        if camera:
                            camera.release()
                        continue

                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
                    camera.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
                    camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

                    # Warm-up read catches backends that open but never deliver frames.
                    ok, _ = camera.read()
                    if not ok:
                        camera.release()
                        continue

                    print(
                        f"[System] Camera opened at index {index} "
                        f"with {backend_name} backend"
                    )
                    return camera
                except Exception as e:
                    print(
                        f"[System] Camera index {index} "
                        f"with backend {backend_name} failed: {e}"
                    )

        return None

    def start(self, mode="hand", voice_enabled=False):
        """Start the control system.

        Returns:
            bool: True if startup succeeded, False otherwise.
        """
        if self.running:
            print("[System] Already running")
            return True

        self.control_mode = mode
        self.voice_enabled = voice_enabled
        print(
            f"[System] Starting in {self.control_mode} mode "
            f"(voice {'on' if self.voice_enabled else 'off'})..."
        )
        self.running = True

        if self.voice_enabled:
            self.voice_controller.start_listening()

        if self.control_mode == "iris":
            # Initialize iris controller for eye tracking
            try:
                self.iris_controller = EyeMouseController()
                # Run iris loop in separate thread
                self.thread = threading.Thread(target=self._iris_main_loop, daemon=True)
                self.thread.start()
                print("[System] Iris (eye-tracking) mode started successfully")
                return True
            except Exception as e:
                print(f"[System] ERROR: Could not start iris mode: {e}")
                print("[System] Falling back to hand gesture mode")
                self.control_mode = "hand"
                # Continue with hand mode below
        
        if self.control_mode == "voice":
            print("[System] Voice-only mode started successfully")
            return True

        # Hand mode or fallback from iris mode
        # Open camera with backend fallback strategy.
        self.camera = self._open_camera()

        if self.camera is None:
            print("[System] ERROR: Could not open camera")
            self.running = False
            return False

        # Setup display
        self.display_manager.setup_window()

        # Run main loop in separate thread
        self.thread = threading.Thread(target=self._hand_main_loop, daemon=True)
        self.thread.start()

        print("[System] Hand mode started successfully")
        return True

    def stop(self):
        """Stop the control system."""
        if not self.running:
            return

        print("[System] Stopping...")
        self.running = False

        # Stop iris mode loop
        if self.iris_controller:
            self.iris_controller.stop()

        # Release camera first to unblock any in-progress camera.read() call.
        if self.camera:
            self.camera.release()
            self.camera = None

        # Wait for thread to finish
        thread_stopped = True
        if hasattr(self, 'thread'):
            self.thread.join(timeout=3)
            thread_stopped = not self.thread.is_alive()

        # Stop voice control
        if self.voice_enabled:
            self.voice_controller.stop_listening()
            self.voice_enabled = False

        # Release resources
        self.iris_controller = None
        with self.frame_lock:
            self.latest_display_frame = None
        if thread_stopped:
            self.gesture_recognizer.close()
        else:
            print("[System] Warning: Worker thread did not stop in time; skipping recognizer close")
        self.display_manager.close()

        print("[System] Stopped")

    def is_running(self):
        """Return current running state for dashboard status sync."""
        return self.running

    def poll_ui_events(self):
        """Pump OpenCV UI events from the main thread for Windows stability."""
        if not self.running or self.control_mode != "hand":
            return

        frame_to_show = None
        with self.frame_lock:
            if self.latest_display_frame is not None:
                frame_to_show = self.latest_display_frame

        if frame_to_show is not None:
            self.display_manager.show_frame(frame_to_show)

        key = self.display_manager.wait_key(1)
        if key == ord('q') or key == 27:  # 'q' or ESC
            print("[System] Quit key pressed")
            self.stop()
            return

        if not self.display_manager.is_window_open():
            print("[System] Camera window closed")
            self.stop()

    def _hand_main_loop(self):
        """Hand-gesture processing loop (runs in separate thread)."""
        last_gesture = config.GESTURE_NONE
        failed_reads = 0

        try:
            while self.running:
                # Refresh active app profile every second.
                now = time.time()
                if now - self.last_profile_update_time >= 1.0:
                    self.active_profile = self.profile_manager.update_active_profile()
                    self.last_profile_update_time = now

                # Read frame
                ret, frame = self.camera.read()
                if not ret:
                    failed_reads += 1
                    if failed_reads >= config.CAMERA_READ_RETRY_LIMIT:
                        print("[System] ERROR: Camera feed not responding")
                        self.running = False
                        break
                    time.sleep(0.05)
                    continue

                failed_reads = 0

                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)

                # Process frame with MediaPipe
                results, rgb_frame = self.gesture_recognizer.process_frame(frame)

                gesture = config.GESTURE_NONE

                # If hand detected
                if results and results.hand_landmarks:
                    # Draw landmarks
                    frame = self.gesture_recognizer.draw_landmarks(frame, results)

                    # First, try two-hand gestures when both hands are present.
                    two_hand_gesture = self.gesture_recognizer.recognize_two_hand_gesture(
                        results.hand_landmarks
                    )

                    # Use first hand for cursor and one-hand gesture path.
                    primary_landmarks = results.hand_landmarks[0]

                    # Get cursor position
                    raw_x, raw_y = self.gesture_recognizer.get_cursor_position(
                        primary_landmarks,
                        config.CAMERA_WIDTH,
                        config.CAMERA_HEIGHT
                    )

                    # Smooth cursor position
                    smooth_x, smooth_y = self.cursor_smoother.smooth(raw_x, raw_y)

                    if two_hand_gesture != config.GESTURE_NONE:
                        gesture = two_hand_gesture
                    else:
                        dynamic_gesture = self.gesture_recognizer.detect_dynamic_gesture(primary_landmarks)
                        if dynamic_gesture != config.GESTURE_NONE:
                            gesture = dynamic_gesture
                        else:
                            gesture = self.gesture_recognizer.recognize_gesture(primary_landmarks)

                    # Execute actions based on gesture
                    self._execute_gesture_action(gesture, smooth_x, smooth_y, last_gesture)

                    last_gesture = gesture

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
                frame = self.display_manager.draw_overlay(
                    frame,
                    gesture,
                    voice_command,
                    self.fps,
                    profile=self.active_profile,
                    dictation=self.voice_controller.dictation_mode
                )

                # Hand off latest frame for main-thread display.
                with self.frame_lock:
                    self.latest_display_frame = frame
        except Exception as e:
            print(f"[System] ERROR in hand loop: {e}")
            self.running = False

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

        profile = self.active_profile

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
                if profile == "browser":
                    self.mouse_controller.browser_forward()
                else:
                    self.presentation_controller.next_slide()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Next slide")

        elif gesture == config.GESTURE_PREV_SLIDE:
            if last_gesture != config.GESTURE_PREV_SLIDE:
                if profile == "browser":
                    self.mouse_controller.browser_back()
                else:
                    self.presentation_controller.previous_slide()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Previous slide")

        elif gesture == config.GESTURE_VOLUME_UP:
            if last_gesture != config.GESTURE_VOLUME_UP:
                self.mouse_controller.volume_up()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Volume up")

        elif gesture == config.GESTURE_VOLUME_DOWN:
            if last_gesture != config.GESTURE_VOLUME_DOWN:
                self.mouse_controller.volume_down()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Volume down")

        elif gesture == config.GESTURE_SWIPE_LEFT:
            if last_gesture != config.GESTURE_SWIPE_LEFT:
                if profile == "presentation":
                    self.presentation_controller.previous_slide()
                else:
                    self.mouse_controller.browser_back()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Swipe left (browser back)")

        elif gesture == config.GESTURE_SWIPE_RIGHT:
            if last_gesture != config.GESTURE_SWIPE_RIGHT:
                if profile == "presentation":
                    self.presentation_controller.next_slide()
                else:
                    self.mouse_controller.browser_forward()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Swipe right (browser forward)")

        elif gesture == config.GESTURE_SWIPE_UP:
            if last_gesture != config.GESTURE_SWIPE_UP:
                if profile == "writing":
                    self.mouse_controller.redo()
                else:
                    self.mouse_controller.maximize_window()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Swipe up (maximize)")

        elif gesture == config.GESTURE_SWIPE_DOWN:
            if last_gesture != config.GESTURE_SWIPE_DOWN:
                if profile == "writing":
                    self.mouse_controller.undo()
                else:
                    self.mouse_controller.minimize_window()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Swipe down (minimize)")

        elif gesture == config.GESTURE_TWO_HAND_LOCK:
            if last_gesture != config.GESTURE_TWO_HAND_LOCK:
                self.mouse_controller.lock_screen()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Two-hand lock screen")

        elif gesture == config.GESTURE_TWO_HAND_ZOOM_IN:
            if last_gesture != config.GESTURE_TWO_HAND_ZOOM_IN:
                self.mouse_controller.zoom_in()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Two-hand zoom in")

        elif gesture == config.GESTURE_TWO_HAND_ZOOM_OUT:
            if last_gesture != config.GESTURE_TWO_HAND_ZOOM_OUT:
                self.mouse_controller.zoom_out()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Two-hand zoom out")

        elif gesture == config.GESTURE_TWO_HAND_COPY:
            if last_gesture != config.GESTURE_TWO_HAND_COPY:
                self.mouse_controller.copy()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Two-hand copy")

        elif gesture == config.GESTURE_TWO_HAND_PASTE:
            if last_gesture != config.GESTURE_TWO_HAND_PASTE:
                self.mouse_controller.paste()
                self.gesture_recognizer.trigger_cooldown()
                print("[Gesture] Two-hand paste")

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
        status_callback=system.is_running,
        ui_event_callback=system.poll_ui_events
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
