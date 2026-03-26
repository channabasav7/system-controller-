"""
Advanced Eye-Tracking Mouse Controller
=======================================
Controls the OS mouse cursor using iris tracking via MediaPipe.

Features:
  - Iris landmark detection (MediaPipe FaceMesh refined)
  - 9-point calibration with polynomial regression mapping
  - Kalman filter for smooth, low-latency cursor movement
  - Blink-based click detection (EAR threshold)
  - Dwell-click fallback
  - Head pose compensation (solvePnP)
  - Configurable via config.yaml

Requirements:
    pip install mediapipe opencv-python pyautogui numpy scipy scikit-learn pynput
"""

import cv2
import numpy as np
import pyautogui
import time
import yaml
import os
import threading
from dataclasses import dataclass, field
from typing import Optional, Tuple, List
from enum import Enum
from collections import deque

# New MediaPipe API
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp

# ── Constants ─────────────────────────────────────────────────────────────────

# MediaPipe FaceMesh landmark indices
IRIS_LEFT_CENTER  = 468
IRIS_RIGHT_CENTER = 473

LEFT_EYE_LANDMARKS  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_LANDMARKS = [33,  160, 158, 133, 153, 144]

# 3D face model points for head pose estimation (generic model)
FACE_3D_MODEL = np.array([
    [0.0,   0.0,    0.0],     # Nose tip
    [0.0,  -330.0, -65.0],    # Chin
    [-225.0, 170.0,-135.0],   # Left eye outer corner
    [225.0,  170.0,-135.0],   # Right eye outer corner
    [-150.0,-150.0,-125.0],   # Left mouth corner
    [150.0, -150.0,-125.0],   # Right mouth corner
], dtype=np.float64)

FACE_2D_INDICES = [1, 152, 263, 33, 287, 57]  # Matching landmarks


# ── Config ────────────────────────────────────────────────────────────────────

@dataclass
class Config:
    # Camera
    camera_index: int = 0
    frame_width:  int = 640
    frame_height: int = 480

    # Gaze mapping
    use_head_pose_compensation: bool = True
    calibration_points: int = 9       # 4, 5, or 9

    # Smoothing (Kalman)
    kalman_process_noise:     float = 1e-3
    kalman_measurement_noise: float = 1e-1

    # EMA fallback smoothing alpha
    ema_alpha: float = 0.25

    # Click detection
    blink_ear_threshold:   float = 0.21   # Eye Aspect Ratio below this = blink
    blink_min_frames:      int   = 2      # Min frames eye must be closed
    blink_cooldown_ms:     int   = 700    # Cooldown between clicks
    dwell_click_enabled:   bool  = True
    dwell_time_ms:         int   = 1200   # Dwell duration for click
    dwell_radius_px:       int   = 40     # Pixel radius to consider "same position"

    # Cursor movement
    cursor_speed_scale:    float = 1.0
    deadzone_px:           int   = 4      # Ignore movements smaller than this

    # Debug overlay
    show_overlay:          bool  = True

    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        cfg = cls()
        for k, v in data.items():
            if hasattr(cfg, k):
                setattr(cfg, k, v)
        return cfg


# ── Kalman Filter ─────────────────────────────────────────────────────────────

class KalmanCursorFilter:
    """2D Kalman filter for smooth cursor position estimation."""

    def __init__(self, process_noise: float = 1e-3, measurement_noise: float = 1e-1):
        self.kf = cv2.KalmanFilter(4, 2)
        dt = 1.0

        # State transition: [x, y, vx, vy]
        self.kf.transitionMatrix = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1],
        ], dtype=np.float32)

        self.kf.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=np.float32)

        self.kf.processNoiseCov     = np.eye(4, dtype=np.float32) * process_noise
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * measurement_noise
        self.kf.errorCovPost        = np.eye(4, dtype=np.float32)
        self._initialized = False

    def update(self, x: float, y: float) -> Tuple[float, float]:
        measurement = np.array([[np.float32(x)], [np.float32(y)]])
        if not self._initialized:
            self.kf.statePre = np.array([[x], [y], [0], [0]], dtype=np.float32)
            self._initialized = True

        self.kf.predict()
        estimated = self.kf.correct(measurement)
        return float(estimated[0][0]), float(estimated[1][0])

    def reset(self):
        self._initialized = False


# ── Eye Aspect Ratio ──────────────────────────────────────────────────────────

def eye_aspect_ratio(landmarks, eye_indices: List[int], img_w: int, img_h: int) -> float:
    """
    EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
    Returns a ratio: ~0.3 open, <0.21 closed/blink
    """
    pts = []
    for idx in eye_indices:
        lm = landmarks[idx]
        pts.append(np.array([lm.x * img_w, lm.y * img_h]))

    # Vertical distances
    A = np.linalg.norm(pts[1] - pts[5])
    B = np.linalg.norm(pts[2] - pts[4])
    # Horizontal distance
    C = np.linalg.norm(pts[0] - pts[3])
    ear = (A + B) / (2.0 * C + 1e-6)
    return ear


# ── Head Pose Estimator ───────────────────────────────────────────────────────

class HeadPoseEstimator:
    """Estimates rotation and translation vectors using solvePnP."""

    def __init__(self, frame_w: int, frame_h: int):
        focal = frame_w
        cx, cy = frame_w / 2.0, frame_h / 2.0
        self.camera_matrix = np.array([
            [focal, 0,     cx],
            [0,     focal, cy],
            [0,     0,      1],
        ], dtype=np.float64)
        self.dist_coeffs = np.zeros((4, 1))

    def estimate(self, landmarks, img_w: int, img_h: int) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        face_2d = []
        for idx in FACE_2D_INDICES:
            lm = landmarks[idx]
            face_2d.append([lm.x * img_w, lm.y * img_h])
        face_2d = np.array(face_2d, dtype=np.float64)

        success, rvec, tvec = cv2.solvePnP(
            FACE_3D_MODEL, face_2d,
            self.camera_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        if not success:
            return None
        return rvec, tvec

    def get_angles(self, rvec: np.ndarray) -> Tuple[float, float, float]:
        """Returns (pitch, yaw, roll) in degrees."""
        rmat, _ = cv2.Rodrigues(rvec)
        sy = np.sqrt(rmat[0, 0]**2 + rmat[1, 0]**2)
        singular = sy < 1e-6
        if not singular:
            pitch = np.degrees(np.arctan2(-rmat[2, 0], sy))
            yaw   = np.degrees(np.arctan2( rmat[1, 0], rmat[0, 0]))
            roll  = np.degrees(np.arctan2( rmat[2, 1], rmat[2, 2]))
        else:
            pitch = np.degrees(np.arctan2(-rmat[2, 0], sy))
            yaw   = 0.0
            roll  = np.degrees(np.arctan2(-rmat[1, 2], rmat[1, 1]))
        return pitch, yaw, roll


# ── Calibration ───────────────────────────────────────────────────────────────

class CalibrationMode(Enum):
    IDLE      = "idle"
    RUNNING   = "running"
    COMPLETE  = "complete"


class Calibrator:
    """
    9-point grid calibration.
    Collects iris positions while user fixates on screen targets.
    Fits a polynomial regression from iris → screen coordinates.
    """

    def __init__(self, screen_w: int, screen_h: int, n_points: int = 9):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.n_points = n_points
        self.targets  = self._generate_targets()
        self.collected_iris: List[np.ndarray] = []
        self.collected_screen: List[np.ndarray] = []
        self.current_idx = 0
        self.state = CalibrationMode.IDLE
        self._samples_per_point = 30
        self._current_samples: List[np.ndarray] = []
        self._model_x = None
        self._model_y = None

    def _generate_targets(self) -> List[Tuple[int, int]]:
        margin = 80
        w, h = self.screen_w, self.screen_h
        if self.n_points == 9:
            xs = [margin, w // 2, w - margin]
            ys = [margin, h // 2, h - margin]
            return [(x, y) for y in ys for x in xs]
        elif self.n_points == 5:
            return [
                (margin, margin),
                (w - margin, margin),
                (w // 2, h // 2),
                (margin, h - margin),
                (w - margin, h - margin),
            ]
        else:  # 4
            return [
                (margin, margin),
                (w - margin, margin),
                (margin, h - margin),
                (w - margin, h - margin),
            ]

    def current_target(self) -> Optional[Tuple[int, int]]:
        if self.current_idx < len(self.targets):
            return self.targets[self.current_idx]
        return None

    def add_sample(self, iris_xy: np.ndarray):
        """Feed one iris sample while user fixates on current target."""
        self._current_samples.append(iris_xy.copy())
        if len(self._current_samples) >= self._samples_per_point:
            # Median is more robust to micro-saccade outliers than mean.
            med = np.median(np.array(self._current_samples), axis=0)
            self.collected_iris.append(med)
            self.collected_screen.append(np.array(self.targets[self.current_idx]))
            self._current_samples.clear()
            self.current_idx += 1
            if self.current_idx >= len(self.targets):
                self._fit()
                self.state = CalibrationMode.COMPLETE

    def _fit(self):
        """Fit a degree-2 polynomial regression for x and y separately."""
        from sklearn.preprocessing import PolynomialFeatures
        from sklearn.linear_model import Ridge

        X = np.array(self.collected_iris)       # (N, 2) — iris x,y
        Sy = np.array([p[0] for p in self.collected_screen])  # screen x
        Sx = np.array([p[1] for p in self.collected_screen])  # screen y

        poly = PolynomialFeatures(degree=2)
        Xp = poly.fit_transform(X)

        self._poly = poly
        # Correct axis mapping: model_x -> screen X, model_y -> screen Y.
        self._model_x = Ridge(alpha=1.0).fit(Xp, Sx)
        self._model_y = Ridge(alpha=1.0).fit(Xp, Sy)

    def map(self, iris_xy: np.ndarray) -> Optional[Tuple[float, float]]:
        if self._model_x is None:
            return None
        Xp = self._poly.transform(iris_xy.reshape(1, -1))
        sx = float(self._model_x.predict(Xp)[0])
        sy = float(self._model_y.predict(Xp)[0])
        return sx, sy

    def progress(self) -> float:
        total_samples = len(self.targets) * self._samples_per_point
        done = (self.current_idx * self._samples_per_point) + len(self._current_samples)
        return done / total_samples

    def reset(self):
        self.collected_iris.clear()
        self.collected_screen.clear()
        self.current_idx = 0
        self._current_samples.clear()
        self._model_x = None
        self._model_y = None
        self.state = CalibrationMode.RUNNING


# ── Click Detector ────────────────────────────────────────────────────────────

class ClickDetector:
    """Detects intentional blinks and dwell clicks."""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._blink_counter   = 0
        self._last_click_time = 0.0
        self._dwell_start     = None
        self._dwell_pos       = None

    def process(
        self,
        left_ear: float,
        right_ear: float,
        cursor_pos: Tuple[float, float],
    ) -> bool:
        """Returns True if a click should fire this frame."""
        now = time.time()
        cooldown = self.cfg.blink_cooldown_ms / 1000.0

        # ── Blink detection ──
        avg_ear = (left_ear + right_ear) / 2.0
        if avg_ear < self.cfg.blink_ear_threshold:
            self._blink_counter += 1
        else:
            if self._blink_counter >= self.cfg.blink_min_frames:
                if (now - self._last_click_time) > cooldown:
                    self._last_click_time = now
                    self._blink_counter = 0
                    return True
            self._blink_counter = 0

        # ── Dwell click ──
        if self.cfg.dwell_click_enabled:
            x, y = cursor_pos
            if self._dwell_pos is None:
                self._dwell_pos  = (x, y)
                self._dwell_start = now
            else:
                dx = abs(x - self._dwell_pos[0])
                dy = abs(y - self._dwell_pos[1])
                if dx < self.cfg.dwell_radius_px and dy < self.cfg.dwell_radius_px:
                    elapsed = (now - self._dwell_start) * 1000
                    if elapsed >= self.cfg.dwell_time_ms:
                        if (now - self._last_click_time) > cooldown:
                            self._last_click_time = now
                            self._dwell_start = now  # reset dwell
                            return True
                else:
                    self._dwell_pos  = (x, y)
                    self._dwell_start = now

        return False

    def dwell_progress(self, cursor_pos: Tuple[float, float]) -> float:
        """Returns 0..1 progress toward dwell click."""
        if not self.cfg.dwell_click_enabled or self._dwell_start is None:
            return 0.0
        x, y = cursor_pos
        if self._dwell_pos:
            dx = abs(x - self._dwell_pos[0])
            dy = abs(y - self._dwell_pos[1])
            if dx > self.cfg.dwell_radius_px or dy > self.cfg.dwell_radius_px:
                return 0.0
        elapsed = (time.time() - self._dwell_start) * 1000
        return min(elapsed / self.cfg.dwell_time_ms, 1.0)


# ── Overlay Renderer ──────────────────────────────────────────────────────────

class OverlayRenderer:
    """Draws debug info onto the webcam preview frame."""

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw(
        self,
        frame: np.ndarray,
        left_ear: float,
        right_ear: float,
        pitch: float, yaw: float, roll: float,
        cursor_pos: Optional[Tuple[float, float]],
        dwell_progress: float,
        fps: float,
        calibration_state: CalibrationMode,
        calibration_target: Optional[Tuple[int, int]],
        calibration_progress: float,
    ):
        h, w = frame.shape[:2]
        overlay = frame.copy()

        # Semi-transparent dark bar at top
        cv2.rectangle(overlay, (0, 0), (w, 110), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        def txt(text, x, y, color=(220, 220, 220), scale=0.45):
            cv2.putText(frame, text, (x, y), self.font, scale, color, 1, cv2.LINE_AA)

        txt(f"FPS: {fps:.1f}", 10, 18)
        txt(f"EAR L:{left_ear:.2f} R:{right_ear:.2f}", 10, 36)
        txt(f"Pose  P:{pitch:+.1f} Y:{yaw:+.1f} R:{roll:+.1f}", 10, 54)

        # Status message
        if calibration_state == CalibrationMode.IDLE:
            status = "Status: IDLE - Waiting for calibration (press C)"
            status_color = (200, 100, 100)
        elif calibration_state == CalibrationMode.RUNNING:
            status = f"Status: CALIBRATING... {calibration_progress*100:.0f}%"
            status_color = (100, 200, 100)
        else:  # COMPLETE
            status = "Status: READY - Eye tracking active"
            status_color = (100, 255, 100)
        
        txt(status, 10, 72, status_color, 0.5)
        
        if cursor_pos:
            txt(f"Cursor: ({cursor_pos[0]:.0f}, {cursor_pos[1]:.0f})", 10, 90, (100, 200, 255))

        # Dwell progress arc
        if dwell_progress > 0.01 and cursor_pos:
            cx, cy = int(cursor_pos[0] * w / pyautogui.size()[0]), \
                     int(cursor_pos[1] * h / pyautogui.size()[1])
            angle = int(360 * dwell_progress)
            cv2.ellipse(frame, (cx, cy), (18, 18), -90, 0, angle, (0, 255, 180), 2)

        # Calibration overlay
        if calibration_state == CalibrationMode.RUNNING and calibration_target:
            # Map screen target → preview window coords
            sw, sh = pyautogui.size()
            tx = int(calibration_target[0] / sw * w)
            ty = int(calibration_target[1] / sh * h)
            cv2.circle(frame, (tx, ty), 18, (0, 200, 255), 2)
            cv2.circle(frame, (tx, ty), 4,  (0, 200, 255), -1)
            # Progress ring
            cv2.ellipse(frame, (tx, ty), (18, 18), -90, 0,
                        int(360 * calibration_progress), (0, 255, 100), 2)
            txt("CALIBRATING — look at circle", w // 2 - 100, h - 20, (0, 200, 255), 0.5)
        
        # Help text at bottom
        txt("[C] Calibrate  [R] Reset  [Q] Quit", 10, h - 10, (200, 200, 200), 0.4)


# ── Main Controller ───────────────────────────────────────────────────────────

class EyeMouseController:
    """
    Orchestrates all components into a real-time control loop.

    Usage:
        ctrl = EyeMouseController()
        ctrl.run()          # blocks; press 'c' to calibrate, 'q' to quit
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        self.cfg = Config.from_yaml(config_path)
        pyautogui.FAILSAFE = False
        self.screen_w, self.screen_h = pyautogui.size()

        # Sub-systems
        self.kalman    = KalmanCursorFilter(self.cfg.kalman_process_noise,
                                            self.cfg.kalman_measurement_noise)
        self.calibrator = Calibrator(self.screen_w, self.screen_h,
                                     self.cfg.calibration_points)
        self.clicker   = ClickDetector(self.cfg)
        self.overlay   = OverlayRenderer()
        self.pose_est  = None  # initialized after first frame

        # MediaPipe - new API (tasks)
        base_options = python.BaseOptions(model_asset_path=self._get_face_landmarker_model())
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1
        )
        self.face_landmarker = vision.FaceLandmarker.create_from_options(options)

        # State
        self._ema_pos: Optional[Tuple[float, float]] = None
        self._prev_cursor: Optional[Tuple[float, float]] = None
        self._fps_deque = deque(maxlen=30)
        self._last_t = time.time()
        self._stop_event = threading.Event()
        self._running = False
        self._face_detected_frames = 0  # Track consecutive frames with face detected
        self._auto_calibration_delayed = False  # Whether auto-calibration timer started

    # ── Iris extraction ───────────────────────────────────────────────────────

    def _get_face_landmarker_model(self) -> str:
        """Get path to face landmarker model. Downloads if needed."""
        try:
            import mediapipe.tasks.python.vision as vision_module
            # Try to get builtin model path
            return "mediapipe/tasks/python/assets/models/face_landmarker.task"
        except:
            pass
        
        # Fallback: check local directory
        model_path = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
        if os.path.exists(model_path):
            return model_path
        
        # If not found, raise error with instructions
        raise FileNotFoundError(
            "\nface_landmarker.task model not found!\n"
            "Download from:\n"
            "https://storage.googleapis.com/mediapipe-assets/face_landmarker.task\n"
            "Place in: " + os.path.dirname(__file__)
        )

    def _get_iris_center(
        self,
        landmarks,
        img_w: int,
        img_h: int,
    ) -> Optional[np.ndarray]:
        """Returns the averaged left+right iris center in image pixels."""
        try:
            lx = landmarks[IRIS_LEFT_CENTER].x  * img_w
            ly = landmarks[IRIS_LEFT_CENTER].y  * img_h
            rx = landmarks[IRIS_RIGHT_CENTER].x * img_w
            ry = landmarks[IRIS_RIGHT_CENTER].y * img_h
            return np.array([(lx + rx) / 2.0, (ly + ry) / 2.0])
        except Exception:
            return None

    # ── Gaze → screen mapping ─────────────────────────────────────────────────

    def _iris_to_screen(
        self,
        iris_xy: np.ndarray,
        rvec: Optional[np.ndarray] = None,
        tvec: Optional[np.ndarray] = None,
    ) -> Optional[Tuple[float, float]]:
        """Map iris pixel position to screen coordinates via calibration model."""
        point = np.array([float(iris_xy[0]), float(iris_xy[1])])

        # Head pose compensation: subtract yaw/pitch contribution
        if self.cfg.use_head_pose_compensation and rvec is not None:
            _, yaw, _ = self.pose_est.get_angles(rvec)
            pitch, _, _ = self.pose_est.get_angles(rvec)
            point[0] -= float(yaw) * 1.5
            point[1] -= float(pitch) * 1.5

        mapped = self.calibrator.map(point)
        if mapped:
            return float(mapped[0]), float(mapped[1])
        return None

    # ── EMA fallback ──────────────────────────────────────────────────────────

    def _ema_smooth(self, x: float, y: float) -> Tuple[float, float]:
        a = self.cfg.ema_alpha
        if self._ema_pos is None:
            self._ema_pos = (x, y)
        ex = a * x + (1 - a) * self._ema_pos[0]
        ey = a * y + (1 - a) * self._ema_pos[1]
        self._ema_pos = (ex, ey)
        return ex, ey

    # ── Move cursor ───────────────────────────────────────────────────────────

    def _move_cursor(self, sx: float, sy: float):
        sx = max(0, min(self.screen_w  - 1, sx))
        sy = max(0, min(self.screen_h  - 1, sy))

        # Deadzone suppression
        if self._prev_cursor:
            dx = abs(sx - self._prev_cursor[0])
            dy = abs(sy - self._prev_cursor[1])
            if dx < self.cfg.deadzone_px and dy < self.cfg.deadzone_px:
                return

        # Kalman smooth
        sx, sy = self.kalman.update(sx, sy)
        # EMA on top for extra stability
        sx, sy = self._ema_smooth(sx, sy)

        pyautogui.moveTo(int(sx), int(sy), duration=0)
        self._prev_cursor = (sx, sy)

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        self._stop_event.clear()
        self._running = True

        cap = cv2.VideoCapture(self.cfg.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.cfg.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.frame_height)
        cap.set(cv2.CAP_PROP_FPS, 30)

        print("\n=== Eye Mouse Controller ===")
        print("  [C]  Start calibration")
        print("  [R]  Reset calibration")
        print("  [Q]  Quit\n")

        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.pose_est = HeadPoseEstimator(frame_w, frame_h)

        while cap.isOpened() and not self._stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)  # Mirror
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w  = frame.shape[:2]

            # ── FPS ──────────────────────────────────────────────────────────
            now = time.time()
            self._fps_deque.append(1.0 / max(now - self._last_t, 1e-6))
            self._last_t = now
            fps = np.mean(self._fps_deque)

            # ── Inference ────────────────────────────────────────────────────
            # Convert frame to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            results = self.face_landmarker.detect(mp_image)

            left_ear = right_ear = 0.3
            pitch = yaw = roll = 0.0
            cursor_pos = self._prev_cursor
            rvec = tvec = None

            if results.face_landmarks:
                # Convert normalized landmarks to pixel coordinates
                lms_data = results.face_landmarks[0]
                lms = []
                for lm in lms_data:
                    # Create a simple object to hold normalized coordinates
                    class Landmark:
                        def __init__(self, x, y, z=0.0):
                            self.x = x
                            self.y = y
                            self.z = z
                    lms.append(Landmark(lm.x, lm.y, lm.z))

                # Track consecutive face detections for auto-calibration
                self._face_detected_frames += 1
                if self._face_detected_frames > 30 and not self._auto_calibration_delayed:
                    # After 1 second of stable face detection, auto-start calibration
                    self.calibrator.reset()
                    self.kalman.reset()
                    self._auto_calibration_delayed = True
                    print("[Auto-calibration started — look at each circle (or press 'C' to restart)]")

                # EAR
                left_ear  = eye_aspect_ratio(lms, LEFT_EYE_LANDMARKS,  w, h)
                right_ear = eye_aspect_ratio(lms, RIGHT_EYE_LANDMARKS, w, h)

                # Head pose
                pose = self.pose_est.estimate(lms, w, h)
                if pose:
                    rvec, tvec = pose
                    pitch, yaw, roll = self.pose_est.get_angles(rvec)

                # Iris center
                iris_xy = self._get_iris_center(lms, w, h)

                if iris_xy is not None:
                    if self.calibrator.state == CalibrationMode.RUNNING:
                        self.calibrator.add_sample(iris_xy)
                        if self.calibrator.state == CalibrationMode.COMPLETE:
                            print("[Calibration complete]")
                    elif self.calibrator.state == CalibrationMode.COMPLETE:
                        mapped = self._iris_to_screen(iris_xy, rvec, tvec)
                        if mapped:
                            sx, sy = mapped
                            sx = sx * self.cfg.cursor_speed_scale
                            sy = sy * self.cfg.cursor_speed_scale
                            self._move_cursor(sx, sy)
                            cursor_pos = (sx, sy)

                            # Click detection
                            if self.clicker.process(left_ear, right_ear, (sx, sy)):
                                pyautogui.click()
                                print(f"[Click] at ({sx:.0f}, {sy:.0f})")
            else:
                # No face detected, reset auto-calibration counter
                self._face_detected_frames = 0

            # Draw iris points
            if self.cfg.show_overlay and results.face_landmarks:
                lms_data = results.face_landmarks[0]
                lms = []
                for lm in lms_data:
                    class Landmark:
                        def __init__(self, x, y, z=0.0):
                            self.x = x
                            self.y = y
                            self.z = z
                    lms.append(Landmark(lm.x, lm.y, lm.z))
                for idx in [IRIS_LEFT_CENTER, IRIS_RIGHT_CENTER]:
                    ix = int(lms[idx].x * w)
                    iy = int(lms[idx].y * h)
                    cv2.circle(frame, (ix, iy), 4, (0, 255, 180), -1)

            # Overlay
            dwell_prog = self.clicker.dwell_progress(cursor_pos) if cursor_pos else 0.0
            if self.cfg.show_overlay:
                self.overlay.draw(
                    frame, left_ear, right_ear, pitch, yaw, roll,
                    cursor_pos, dwell_prog, fps,
                    self.calibrator.state,
                    self.calibrator.current_target(),
                    self.calibrator.progress(),
                )

            cv2.imshow("Eye Mouse Controller", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.calibrator.reset()
                self.kalman.reset()
                print("[Calibration started — look at each circle]")
            elif key == ord('r'):
                self.calibrator = Calibrator(self.screen_w, self.screen_h,
                                             self.cfg.calibration_points)
                self.kalman.reset()
                print("[Calibration reset]")

        cap.release()
        cv2.destroyAllWindows()
        if hasattr(self, 'face_landmarker'):
            del self.face_landmarker
        self._running = False

    def stop(self):
        """Request controller loop to stop from external callers."""
        self._stop_event.set()

    @property
    def is_running(self) -> bool:
        return self._running


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    controller = EyeMouseController()
    controller.run()
