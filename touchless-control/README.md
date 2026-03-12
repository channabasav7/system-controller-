# 🖐️ Touchless Laptop Control System

**Control your laptop using hand gestures and voice commands!**

A Python-based system that enables touchless interaction with your computer through real-time hand gesture recognition (using MediaPipe and OpenCV) and voice command processing (using SpeechRecognition).

---

## 📋 Features

### Hand Gesture Control
- **Move Cursor**: Point with your index finger to control the mouse
- **Left Click**: Touch index finger and thumb together
- **Right Click**: Touch thumb and middle finger together
- **Drag & Drop**: Pinch and hold (index + thumb) to drag items
- **Scroll Up/Down**: Use two fingers and move vertically
- **Next/Previous Slide**: Use three fingers and swipe up/down

### Voice Command Control
Supported voice commands:
- `"Open Chrome"` - Launch Google Chrome
- `"Open PowerPoint"` - Launch Microsoft PowerPoint
- `"Next Slide"` / `"Previous Slide"` - Navigate presentations
- `"Scroll Up"` / `"Scroll Down"` - Scroll content
- `"Close Window"` - Close active window
- `"Start Presentation"` - Begin slideshow (F5)
- `"Stop Presentation"` - Exit slideshow
- `"Minimize"` / `"Maximize"` - Window management
- `"Open Notepad"` / `"Open Calculator"` - Launch apps
- `"Take Screenshot"` - Capture screen

### Additional Features
- Real-time visual feedback with hand landmarks overlay
- FPS counter and gesture status display
- Cursor smoothing algorithm for stable control
- GUI dashboard for settings and control
- Multithreaded architecture for simultaneous gesture and voice processing

---

## 🛠️ System Requirements

- **Operating System**: Windows 10/11 (tested)
- **Python**: 3.10 or higher
- **Webcam**: Any USB or built-in camera
- **Microphone**: Required for voice commands
- **RAM**: Minimum 4GB (8GB recommended)
- **Processor**: Multi-core recommended for smooth performance

---

## 📦 Installation

### Option 1: Automated Setup (Recommended)

1. **Clone or download this repository**
2. **Navigate to the project folder**
3. **Run the setup script**:
   ```powershell
   .\setup.bat
   ```

The script will automatically:
- Check Python installation
- Create a virtual environment
- Install all dependencies
- Set up the project

### Option 2: Manual Setup

1. **Ensure Python 3.10+ is installed**:
   ```powershell
   python --version
   ```

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Install PyAudio** (special case for Windows):
   
   If PyAudio installation fails, download the appropriate wheel file from:
   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   
   Then install it:
   ```powershell
   pip install PyAudio-0.2.14-cp310-cp310-win_amd64.whl
   ```

---

## 🚀 Usage

### Starting the Application

1. **Activate virtual environment** (if created):
   ```powershell
   .\venv\Scripts\activate
   ```

2. **Run the main script**:
   ```powershell
   python main.py
   ```

3. **Use the dashboard**:
   - Click **"Start System"** to begin
   - Enable **"Voice Control"** checkbox for voice commands
   - Adjust **"Cursor Smoothing"** slider for sensitivity

4. **Control with gestures**:
   - Position your hand in front of the webcam
   - The system will detect and display hand landmarks
   - Perform gestures to control the mouse

5. **Exit**:
   - Press `q` in the video window, or
   - Click **"Stop System"** in the dashboard

---

## 🎮 Gesture Guide

| Gesture | Hand Position | Action |
|---------|---------------|--------|
| **Move Cursor** | Index finger extended | Controls mouse pointer |
| **Left Click** | Touch index finger tip to thumb tip | Single left click |
| **Right Click** | Touch middle finger tip to thumb tip | Single right click |
| **Drag & Drop** | Hold index+thumb pinch for 5 frames | Drag mode activated |
| **Scroll Up** | Extend index+middle, move up | Scrolls content up |
| **Scroll Down** | Extend index+middle, move down | Scrolls content down |
| **Next Slide** | Three fingers up, swipe up | PowerPoint next slide |
| **Previous Slide** | Three fingers up, swipe down | PowerPoint previous slide |

---

## 📁 Project Structure

```
touchless-control/
│
├── config.py                    # Configuration constants and settings
├── utils.py                     # Utility functions (smoothing, finger detection)
├── gesture_control.py           # MediaPipe gesture recognition
├── mouse_controller.py          # PyAutoGUI mouse/keyboard control
├── presentation_controller.py   # PowerPoint control
├── voice_control.py             # Speech recognition and commands
├── display.py                   # OpenCV video overlay
├── dashboard.py                 # Tkinter GUI dashboard
├── main.py                      # Main entry point
├── requirements.txt             # Python dependencies
├── setup.bat                    # Automated setup script
└── README.md                    # This file
```

---

## ⚙️ Configuration

You can customize the system by editing `config.py`:

### Camera Settings
```python
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
```

### Gesture Thresholds
```python
TOUCH_THRESHOLD = 0.045          # Distance for touch detection
SCROLL_MOVE_THRESHOLD = 0.03     # Minimum scroll movement
GESTURE_HOLD_FRAMES = 3          # Frames to confirm gesture
```

### Cursor Smoothing
```python
SMOOTHING_FACTOR = 0.4           # 0 = max smooth, 1 = no smoothing
DEAD_ZONE_RADIUS = 5             # Ignore movements smaller than this
```

### Voice Commands
Add custom commands in the `VOICE_COMMANDS` dictionary:
```python
VOICE_COMMANDS = {
    "your phrase": "command_name",
    ...
}
```

---

## 🐛 Troubleshooting

### Camera not detected
- Ensure your webcam is connected and not being used by another application
- Try changing `CAMERA_INDEX` in `config.py` (usually 0, 1, or 2)

### PyAudio installation fails
- Download the pre-built wheel from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- Install manually: `pip install PyAudio‑0.2.14‑cp310‑cp310‑win_amd64.whl`

### Voice commands not working
- Check microphone permissions in Windows Settings
- Ensure you have an active internet connection (Google Speech API)
- Speak clearly and wait for the system to process

### Gestures not detected
- Ensure good lighting conditions
- Keep your hand within the camera frame
- Adjust MediaPipe confidence thresholds in `config.py`

### Performance issues
- Reduce camera resolution in `config.py`
- Close other resource-intensive applications
- Lower MediaPipe confidence thresholds

---

## 🔬 Technical Details

### Architecture
- **Main Thread**: Tkinter GUI dashboard
- **Gesture Thread**: Camera capture and gesture processing
- **Voice Thread**: Continuous speech recognition

### Key Technologies
- **OpenCV**: Camera capture and image processing
- **MediaPipe Hands**: 21-point hand landmark detection
- **PyAutoGUI**: System-level mouse/keyboard control
- **SpeechRecognition**: Voice-to-text conversion
- **Tkinter**: GUI dashboard

### Hand Landmark Model
MediaPipe Hands detects 21 landmarks per hand:
```
0: WRIST
1-4: THUMB (CMC, MCP, IP, TIP)
5-8: INDEX (MCP, PIP, DIP, TIP)
9-12: MIDDLE (MCP, PIP, DIP, TIP)
13-16: RING (MCP, PIP, DIP, TIP)
17-20: PINKY (MCP, PIP, DIP, TIP)
```

---

## 📝 Future Enhancements

Potential additions:
- [ ] Multi-hand gesture support
- [ ] Custom gesture training
- [ ] On-screen annotation tools
- [ ] Virtual keyboard
- [ ] Gesture-based window management
- [ ] Eye tracking integration
- [ ] Offline voice recognition
- [ ] Recording and playback of gesture sequences

---

## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is created for educational purposes as part of a major project.

---

## 👥 Authors

Created as a 6th semester major project.

---

## 🙏 Acknowledgments

- **MediaPipe** by Google for hand tracking technology
- **OpenCV** community for computer vision tools
- **PyAutoGUI** for system control capabilities
- All open-source contributors

---

## 📞 Support

For issues or questions:
1. Check the **Troubleshooting** section above
2. Review configuration in `config.py`
3. Ensure all dependencies are installed correctly
4. Check Python and library versions

---

**Enjoy touchless control! 🖐️✨**
