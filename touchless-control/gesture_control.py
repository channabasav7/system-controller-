"""
Gesture recognition module using MediaPipe Hands.

Handles real‑time hand detection, landmark extraction, and gesture
classification based on finger states and landmark distances.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import config
from utils import get_fingers_up, count_fingers, euclidean_distance


class GestureRecognizer:
    """
    Detects and recognizes hand gestures using MediaPipe Hands.
    """

    def __init__(self):
        """Initialize MediaPipe Hands and internal state."""
        # Initialize MediaPipe Hand Landmarker using synchronous mode
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MP_MAX_HANDS,
            running_mode=vision.RunningMode.IMAGE
        )
        self.hands = vision.HandLandmarker.create_from_options(options)

        # Internal state for gesture stability
        self.current_gesture = config.GESTURE_NONE
        self.gesture_hold_count = 0
        self.cooldown_counter = 0

        # Drag state
        self.drag_active = False
        self.drag_hold_count = 0

        # Scroll reference position
        self.scroll_ref_y = None

    def process_frame(self, frame):
        """
        Process a single frame and detect hands.

        Args:
            frame: BGR image from OpenCV

        Returns:
            (results, rgb_frame): MediaPipe results and RGB‑converted frame
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.hands.detect(mp_image)
        return results, rgb_frame

    def recognize_gesture(self, landmarks):
        """
        Recognize a gesture from hand landmarks.

        Args:
            landmarks: list of 21 MediaPipe hand landmarks

        Returns:
            str: detected gesture name from config.GESTURE_*
        """
        fingers_up = get_fingers_up(landmarks)
        num_fingers = count_fingers(fingers_up)

        # ────────────── Calculate key distances ──────────────────────────────
        # Index finger tip (8) to thumb tip (4)
        index_thumb_dist = euclidean_distance(
            (landmarks[8].x, landmarks[8].y),
            (landmarks[4].x, landmarks[4].y)
        )

        # Middle finger tip (12) to thumb tip (4)
        middle_thumb_dist = euclidean_distance(
            (landmarks[12].x, landmarks[12].y),
            (landmarks[4].x, landmarks[4].y)
        )

        # ────────────── Gesture classification ───────────────────────────────
        # Priority: drag > clicks > scroll > slide > move

        # 1. Pinch (index + thumb) → Drag or Left Click
        if index_thumb_dist < config.TOUCH_THRESHOLD:
            if not self.drag_active:
                self.drag_hold_count += 1
                if self.drag_hold_count >= config.DRAG_START_FRAMES:
                    self.drag_active = True
                    return config.GESTURE_DRAG
            else:
                return config.GESTURE_DRAG
        else:
            if self.drag_active:
                self.drag_active = False
            self.drag_hold_count = 0

            # 2. Index finger only → Left Click
            if fingers_up[1] and not fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
                return config.GESTURE_LEFT_CLICK

            # 3. Index + thumb (not pinched) → Right Click
            if fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
                return config.GESTURE_RIGHT_CLICK

            # 4. Two fingers up (index + middle) → Scroll Up
            if fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
                return config.GESTURE_SCROLL_UP

            # 5. Five fingers up → Scroll Down
            if fingers_up[0] and fingers_up[1] and fingers_up[2] and fingers_up[3] and fingers_up[4]:
                return config.GESTURE_SCROLL_DOWN

            # 6. Peace sign (index + middle, spread) → Next Slide
            if fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
                index_middle_dist = euclidean_distance(
                    (landmarks[8].x, landmarks[8].y),
                    (landmarks[12].x, landmarks[12].y)
                )
                if index_middle_dist > config.PEACE_THRESHOLD:
                    return config.GESTURE_NEXT_SLIDE

            # 7. Three fingers up (spread) → Previous Slide
            if fingers_up[1] and fingers_up[2] and fingers_up[3] and not fingers_up[4]:
                three_finger_dist = euclidean_distance(
                    (landmarks[8].x, landmarks[8].y),
                    (landmarks[16].x, landmarks[16].y)
                )
                if three_finger_dist > config.PEACE_THRESHOLD:
                    return config.GESTURE_PREV_SLIDE

        # 8. Default → Move cursor
        return config.GESTURE_MOVE

    def get_cursor_position(self, landmarks, frame_width, frame_height):
        """
        Get screen coordinates from hand landmarks.

        Args:
            landmarks: list of 21 MediaPipe hand landmarks
            frame_width: width of the camera frame
            frame_height: height of the camera frame

        Returns:
            (x, y): screen coordinates
        """
        # Use index finger MCP (knuckle) for cursor position
        cursor_landmark = landmarks[5]

        # Convert normalized coordinates to screen coordinates
        screen_x = int(cursor_landmark.x * config.SCREEN_WIDTH)
        screen_y = int(cursor_landmark.y * config.SCREEN_HEIGHT)

        # Invert X for natural movement
        screen_x = config.SCREEN_WIDTH - screen_x

        return screen_x, screen_y

    def draw_landmarks(self, frame, results):
        """
        Draw hand landmarks on the frame.

        Args:
            frame: BGR image
            results: MediaPipe results object

        Returns:
            frame with landmarks drawn
        """
        if results and results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                # Draw landmarks using MediaPipe's drawing utilities from vision module
                vision.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    vision.HandLandmarksConnections.HAND_CONNECTIONS,
                    vision.drawing_styles.get_default_hand_landmarks_style(),
                    vision.drawing_styles.get_default_hand_connections_style()
                )

        return frame

    def is_on_cooldown(self):
        """Check if gesture recognition is on cooldown."""
        return self.cooldown_counter > 0

    def trigger_cooldown(self):
        """Start cooldown after a click gesture."""
        self.cooldown_counter = config.ACTION_COOLDOWN_FRAMES

    def update_cooldown(self):
        """Update cooldown counter."""
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

    def close(self):
        """Release MediaPipe resources."""
        if self.hands:
            self.hands.close()