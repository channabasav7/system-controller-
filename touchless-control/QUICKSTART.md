# 🚀 Quick Start Guide

## Installation (5 minutes)

### Step 1: Run Setup
```powershell
.\setup.bat
```
This will:
- Create a virtual environment
- Install all dependencies
- Prepare the system

### Step 2: Launch Application
```powershell
.\run.bat
```
Or manually:
```powershell
.\venv\Scripts\activate
python main.py
```

---

## First Time Usage

### 1. Dashboard Opens
- A GUI window will appear
- Click **"▶ Start System"**

### 2. Camera Window Opens
- Your webcam feed appears
- Hand landmarks are drawn in yellow
- Position your hand in front of the camera

### 3. Try Basic Gestures

**Move Cursor:**
- Extend only your **index finger**
- Move your hand around
- Watch the cursor follow

**Left Click:**
- Touch **index finger tip** to **thumb tip**
- Release to complete click

**Scroll:**
- Extend **index + middle fingers**
- Move hand **up** (scroll up) or **down** (scroll down)

### 4. Enable Voice Control (Optional)
- Check **"Enable Voice Commands"** in dashboard
- Say: **"Open Notepad"**
- System will launch Notepad

---

## Common Issues

### Camera Not Working?
- Close other apps using the camera (Zoom, Teams, etc.)
- Check camera permissions in Windows Settings

### Gestures Not Detected?
- Ensure **good lighting**
- Keep hand **within camera frame**
- Try different camera angles

### PyAudio Installation Failed?
Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```powershell
pip install PyAudio-0.2.14-cp310-cp310-win_amd64.whl
```

---

## Gesture Cheat Sheet

| Gesture | How To | Result |
|---------|--------|--------|
| 👆 **Move** | Index finger up | Cursor moves |
| 🤏 **Click** | Index + Thumb touch | Left click |
| 🤞 **Right Click** | Middle + Thumb touch | Right click |
| ✌️ **Scroll** | 2 fingers, move up/down | Scrolls page |
| 🤟 **Slide** | 3 fingers, swipe up/down | Next/Prev slide |

---

## Voice Command Examples

Say these clearly:
- **"Open Chrome"**
- **"Open PowerPoint"**
- **"Next Slide"**
- **"Scroll Down"**
- **"Close Window"**
- **"Take Screenshot"**

---

## Exit the Application

Press **`q`** in the video window, or click **"⏹ Stop System"** in dashboard.

---

## Need Help?

See full documentation in **README.md**

---

**Happy Gesture Controlling! 🖐️**
