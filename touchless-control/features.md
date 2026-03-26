Touchless Control - Feature Matrix
==================================

Quick Start
-----------

```bash
# Setup
setup.bat

# Run
python main.py
# or
run.bat
```

Implemented (Current Repository)
--------------------------------

Hand Gestures
- Cursor movement (single-hand)
- Left click, right click, drag and drop
- Scroll up/down
- Slide navigation (next/previous)
- Volume up/down by thumb gestures
- Dynamic swipes:
  - Swipe left: browser back (presentation profile: previous slide)
  - Swipe right: browser forward (presentation profile: next slide)
  - Swipe up: maximize (writing profile: redo)
  - Swipe down: minimize (writing profile: undo)
- Two-hand gestures:
  - Both palms open: lock screen
  - Hands spread: zoom in
  - Hands close together: zoom out
  - One fist + one pinch: copy
  - Two fists: paste

Voice Commands
- Presentation:
  - next slide, previous slide
  - start presentation, stop/end presentation
  - go to slide N
  - black screen
- System:
  - take screenshot, close window, minimize, maximize
  - volume up, volume down, mute
  - lock screen, switch window, open task manager
- Editing:
  - copy, paste, select all, undo, redo
  - bold, italic, underline
  - align left, center
  - save document, new paragraph
  - zoom in, zoom out
- Apps:
  - open browser/chrome
  - open powerpoint
  - open notepad
  - open calculator

Special Modes
- Dictation mode by voice:
  - start dictation
  - stop dictation
- App-aware profile selection:
  - Auto profile detection by active window title
  - Manual profile switch by voice:
    - presentation mode
    - browser mode
    - writing mode
    - default mode

Active Profiles
---------------

- default
- presentation
- browser
- writing

Profile mapping is auto-detected from foreground window title and can be manually overridden by voice.

Planned / Stretch Features
--------------------------

- Offline voice recognition (Whisper)
- Wake-word activation
- Virtual keyboard
- Drawing overlay
- Zone-based control UI
- Gesture macro recorder
- Custom gesture trainer
- Multi-language voice support
- Accessibility presets
- Fatigue/emotion detection

Notes
-----

- This file reflects only what is implemented in this repository today under "Implemented".
- Planned features are listed separately to avoid confusion during demos and testing.
