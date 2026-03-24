# Eye-Tracking Mouse Controller

Control your OS mouse cursor using your eyes via webcam.

## Features

| Feature | Details |
|---|---|
| Face landmark detection | MediaPipe FaceMesh (refined — 478 landmarks + iris) |
| Gaze mapping | 9-point polynomial regression calibration |
| Smoothing | Cascaded Kalman filter + EMA |
| Head pose correction | solvePnP — removes drift from head movement |
| Click: blink | Eye Aspect Ratio threshold detection |
| Click: dwell | Gaze-hold timer (configurable duration) |
| Debug overlay | FPS, EAR, head pose angles, dwell arc |
| Config | `config.yaml` — all parameters editable at runtime |

---

## Installation

```bash
pip install mediapipe opencv-python pyautogui numpy scipy scikit-learn pynput
```

> Python 3.9–3.11 recommended. MediaPipe may not support 3.12+ on all platforms.

---

## Usage

```bash
python eye_tracker.py
```

### Keyboard controls (in the webcam preview window)

| Key | Action |
|---|---|
| `C` | Start / restart calibration |
| `R` | Reset calibration data |
| `Q` | Quit |

---

## Calibration

1. Press `C` to start calibration.
2. A circle appears at each of 9 screen positions. **Look at each circle** until it fills up (30-frame average collected).
3. After the 9th point, calibration is complete and the cursor becomes active.

Recalibrate if you move your head or the camera.

---

## Tuning Tips

**Cursor too shaky?**
- Decrease `kalman_process_noise` (e.g. `0.0005`)
- Decrease `ema_alpha` (e.g. `0.15`)
- Increase `deadzone_px` (e.g. `8`)

**Cursor too sluggish / laggy?**
- Increase `ema_alpha` (e.g. `0.4`)
- Increase `kalman_process_noise`

**Accidental clicks?**
- Increase `blink_ear_threshold` (e.g. `0.19`)
- Increase `blink_min_frames` (e.g. `3`)
- Increase `blink_cooldown_ms` (e.g. `1000`)
- Disable dwell click: `dwell_click_enabled: false`

**Cursor drifts when you move head?**
- Ensure `use_head_pose_compensation: true`
- Recalibrate in your natural seated position

---

## Architecture

```
Webcam frames
    │
    ▼
MediaPipe FaceMesh (refine_landmarks=True)
    │
    ├──► Iris landmarks (468, 473) ──► HeadPoseEstimator (solvePnP)
    │         │                               │
    │         │    pose compensation ◄────────┘
    │         ▼
    │    Calibrator.map()  (polynomial regression)
    │         │
    │         ▼
    │    Kalman filter → EMA → pyautogui.moveTo()
    │
    └──► EAR (Eye Aspect Ratio) ──► ClickDetector ──► pyautogui.click()
              └──► Dwell timer ──────────────────────►
```

---

## File Structure

```
eye_mouse_controller/
├── eye_tracker.py   — main controller (all components)
├── config.yaml      — all tunable parameters
└── README.md        — this file
```
