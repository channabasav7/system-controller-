"""
Gesture recognition module using MediaPipe Hands.

Handles real‑time hand detection, landmark extraction, and gesture
classification based on finger states and landmark distances.
"""

import cv2
import mediapipe as mp
import mediapipe.solutions
import mediapipe.solutions.drawing_utils
import mediapipe.solutions.drawing_styles
import mediapipe.solutions.hands
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import config
from utils import get_fingers_up, count_fingers, euclidean_distance


class GestureRecognizer:
    """
    Detects and recognizes hand gestures using MediaPipe Hands.
    """

    def __init__(self):
        """Initialize MediaPipe Hands and internal state."""
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=config.MP_MAX_HANDS)
        self.hands = vision.HandLandmarker.create_from_options(options)
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

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
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True
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
                    return config.GESTURE_LEFT_CLICK
            else:
                return config.GESTURE_DRAG
        else:
            # Release pinch
            if self.drag_active:
                self.drag_active = False
            self.drag_hold_count = 0

        # 2. Thumb + middle finger → Right Click
        if middle_thumb_dist < config.TOUCH_THRESHOLD:
            return config.GESTURE_RIGHT_CLICK

        # 3. Three fingers up + moving vertically → Next/Previous Slide
        if num_fingers == 3:
            # Check vertical movement direction
            index_y = landmarks[8].y
            middle_y = landmarks[12].y
            ring_y = landmarks[16].y
            avg_y = (index_y + middle_y + ring_y) / 3

            if self.scroll_ref_y is None:
                self.scroll_ref_y = avg_y
            else:
                delta_y = avg_y - self.scroll_ref_y
                if abs(delta_y) > config.SCROLL_MOVE_THRESHOLD:
                    self.scroll_ref_y = avg_y
                    if delta_y < 0:
                        return config.GESTURE_NEXT_SLIDE
                    else:
                        return config.GESTURE_PREV_SLIDE

        # 4. Two fingers up (index + middle) + moving vertically → Scroll
        elif num_fingers == 2 and fingers_up[1] and fingers_up[2]:
            index_y = landmarks[8].y
            middle_y = landmarks[12].y
            avg_y = (index_y + middle_y) / 2

            if self.scroll_ref_y is None:
                self.scroll_ref_y = avg_y
            else:
                delta_y = avg_y - self.scroll_ref_y
                if abs(delta_y) > config.SCROLL_MOVE_THRESHOLD:
                    self.scroll_ref_y = avg_y
                    if delta_y > 0:
                        return config.GESTURE_SCROLL_DOWN
                    else:
                        return config.GESTURE_SCROLL_UP

        # 5. Index finger only → Move Cursor
        elif num_fingers == 1 and fingers_up[1]:
            self.scroll_ref_y = None
            return config.GESTURE_MOVE

        # Default
        self.scroll_ref_y = None
        return config.GESTURE_NONE

    def get_cursor_position(self, landmarks, frame_width, frame_height):
        """
        Get the cursor position based on index finger tip.

        Args:
            landmarks: list of MediaPipe hand landmarks
            frame_width: int, camera frame width
            frame_height: int, camera frame height

        Returns:
            (screen_x, screen_y): tuple of screen coordinates
        """
        # Use index finger tip (landmark 8)
        index_tip = landmarks[8]

        # Map from camera coordinates to screen coordinates
        # Invert x to mirror the image
        screen_x = int((1 - index_tip.x) * config.SCREEN_WIDTH)
        screen_y = int(index_tip.y * config.SCREEN_HEIGHT)

        # Clamp to screen bounds
        screen_x = max(0, min(config.SCREEN_WIDTH - 1, screen_x))
        screen_y = max(0, min(config.SCREEN_HEIGHT - 1, screen_y))

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
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                # Draw landmarks using the new MediaPipe API
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList(
                    landmark=[
                        landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
                        for lm in hand_landmarks
                    ]
                )
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks_proto,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style()
                )
        return frame

    def update_cooldown(self):
        """Decrement cooldown counter if active."""
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

    def is_on_cooldown(self):
        """Check if gesture actions are on cooldown."""
        return self.cooldown_counter > 0

    def trigger_cooldown(self):
        """Start cooldown after an action."""
        self.cooldown_counter = config.ACTION_COOLDOWN_FRAMES

    def close(self):
        """Release MediaPipe resources."""
        self.hands.close()
