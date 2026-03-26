# 📖 Touchless Control - Complete User Guide

A comprehensive guide to control your laptop using hand gestures and voice commands - completely touchless!

---

## 🚀 Quick Start (2 Minutes)

### Step 1: Launch the Application
```powershell
# From the project root directory
python main.py
# or use the batch file
.\run.bat
```

### Step 2: Verify Your Setup
- **Dashboard window** opens (system settings)
- **Camera window** opens (your webcam feed with hand tracking)
- Your hands appear as yellow landmarks on the camera feed

### Step 3: Start Using
- **Perform a gesture** (point with index finger)
- **Enable voice** (say "start dictation" to test)
- **Watch the overlay** for current profile and mode status

---

## 🖐️ Hand Gesture Reference

### Basic Gestures (Single Hand)

#### 1. **Cursor Movement** 
| Gesture | How To | Result |
|---------|--------|--------|
| 👆 Point | Extend **index finger only** | Cursor moves to finger position |
| | Move hand smoothly | Cursor follows in real-time |

**Tips:**
- Keep your hand in the camera frame
- Point at the target on screen, then perform click
- Good lighting improves accuracy

---

#### 2. **Clicks**
| Gesture | How To | Result |
|---------|--------|--------|
| 🤏 **Left Click** | Touch **index finger** to **thumb** | Performs left click |
| 🤏 **Right Click** | Touch **middle finger** to **thumb** | Performs right click |

**Example workflow:**
1. Point index finger at button
2. Touch index to thumb (click)
3. Release hand to open

---

#### 3. **Drag and Drop**
| Gesture | How To | Result |
|---------|--------|--------|
| ✊ **Drag** | Pinch **index + thumb** and hold | Enters drag mode |
| | Move hand while holding | Drags selected item |
| | Release pinch | Drops item at new location |

**Example workflow:**
1. Point at file/item
2. Pinch index + thumb (start drag)
3. Move hand to new location
4. Release pinch (drop)

---

#### 4. **Scroll**
| Gesture | How To | Result |
|---------|--------|--------|
| ✌️ **Scroll Up** | Extend **index + middle fingers** | Hold gesture and move hand UP |
| ✌️ **Scroll Down** | Extend **index + middle fingers** | Hold gesture and move hand DOWN |

**Example workflow:**
- Web page scrolling:
  1. Open website
  2. Extend 2 fingers upward → page scrolls up
  3. Extend 2 fingers downward → page scrolls down

---

#### 5. **Volume Control**
| Gesture | How To | Result |
|---------|--------|--------|
| 👎 **Volume Down** | Thumb pointing DOWN | System volume decreases |
| 👍 **Volume Up** | Thumb pointing UP | System volume increases |

---

#### 6. **Dynamic Swipes** (Motion-Based)
Detected when you move your hand quickly in a direction.

| Swipe | How To | Result |
|-------|--------|--------|
| → **Swipe Right** | Move hand RIGHT with 2+ fingers extended | Browser: forward; Presentation: next slide |
| ← **Swipe Left** | Move hand LEFT with 2+ fingers extended | Browser: back; Presentation: previous slide |
| ↑ **Swipe Up** | Move hand UP with 2+ fingers extended | Writing mode: redo; Default: maximize |
| ↓ **Swipe Down** | Move hand DOWN with 2+ fingers extended | Writing mode: undo; Default: minimize |

**Pro Tip:** Swipe behavior changes based on active profile (see Profile Modes section)

---

#### 7. **Presentation Slide Navigation**
| Gesture | How To | Result |
|--------|--------|--------|
| 🖐️ **Slide Navigation** | Extend **3 fingers** and hold, then swipe UP/DOWN | Move to next/previous slide |

**Example workflow:**
- Presenting in PowerPoint:
  1. Point 3 fingers at slide area
  2. Swipe upward → next slide
  3. Swipe downward → previous slide

---

### Advanced Gestures (Two Hands)

Use both hands for powerful multi-hand commands. Enable two-hand mode by using both hands in front of camera.

#### 1. **Lock Screen**
| Gesture | How To | Result |
|---------|--------|--------|
| 🤲 **Palms Open** | Both hands with **palms facing outward** | Locks Windows screen |
| | Hold position for 0.5 seconds | User must enter password to unlock |

**Use case:** Quick lock when leaving desk

---

#### 2. **Zoom Controls**
| Gesture | How To | Result |
|---------|--------|--------|
| 🙌 **Zoom In** | Both hands with **fingers spread far apart** | Zooms in (Ctrl++) |
| | Bring hands closer | Can zoom multiple times |
| 🤝 **Zoom Out** | Both hands close together with **fingers together** | Zooms out (Ctrl+-) |
| | Spread hands apart | Can zoom multiple times |

**Use case:** Zoom in on document text or zoom out for overview

---

#### 3. **Copy & Paste**
| Gesture | How To | Result |
|---------|--------|--------|
| 📋 **Copy** | **One hand pinched** (fist) + **other hand pinched** | Copies selected text (Ctrl+C) |
| 📋 **Paste** | Both hands **fully closed as fists** | Pastes clipboard content (Ctrl+V) |

**Workflow example:**
1. Select text with cursor + left click
2. Pinch one hand (copy gesture)
3. Click new location
4. Make two fists (paste gesture)

---

## 🎤 Voice Command Reference

Say commands **clearly and at normal volume**. System listens continuously in the background.

### Presentation Commands
```
"next slide"              → Move to next slide
"previous slide"          → Move to previous slide
"go to slide 5"          → Jump to slide number 5
"start presentation"      → Start slideshow (F5)
"stop presentation"       → Exit slideshow
"black screen"           → Show black screen during presentation
```

### System Commands
```
"take screenshot"        → Capture screen to clipboard
"close window"           → Close active window
"minimize"               → Minimize active window
"maximize"               → Maximize active window
"lock screen"            → Lock Windows
"switch window"          → Switch between windows (Alt+Tab)
"open task manager"      → Open Task Manager
```

### Audio Commands
```
"volume up"              → Increase system volume
"volume down"            → Decrease system volume
"mute"                   → Mute audio
```

### Editing & Formatting
```
"copy"                   → Copy selected text (Ctrl+C)
"paste"                  → Paste clipboard (Ctrl+V)
"select all"             → Select all (Ctrl+A)
"undo"                   → Undo last action (Ctrl+Z)
"redo"                   → Redo last action (Ctrl+Y)
"bold"                   → Make text bold (Ctrl+B)
"italic"                 → Make text italic (Ctrl+I)
"underline"              → Underline text (Ctrl+U)
"align left"             → Left align text (Ctrl+L)
"center"                 → Center align text (Ctrl+E)
"save document"          → Save file (Ctrl+S)
"new paragraph"          → Create new paragraph (Enter x2)
"zoom in"                → Zoom in (Ctrl++)
"zoom out"               → Zoom out (Ctrl+-)
```

### Application Launchers
```
"open browser"           → Open default web browser
"open chrome"            → Open Google Chrome
"open powerpoint"        → Open PowerPoint
"open notepad"           → Open Notepad
"open word"              → Open Microsoft Word
"open calculator"        → Open Calculator
```

### Navigation
```
"browser back"           → Go back in browser (Alt+Left)
"browser forward"        → Go forward in browser (Alt+Right)
```

---

## 👤 Profile Modes

The system automatically detects your active application and switches profiles accordingly. Each profile changes how gestures and commands work.

### 🎯 **Default Mode**
- **Active when:** General Windows activities
- **Gesture behavior:**
  - Swipe up → Maximize window
  - Swipe down → Minimize window
- **Use for:** General browsing, document reading, casual use

---

### 🖥️ **Browser Mode**
- **Active when:** Chrome, Firefox, Edge, Safari are open
- **Gesture behavior:**
  - Swipe left → Go back (browser history)
  - Swipe right → Go forward (browser history)
  - Gesture shortcuts for navigation
- **Use for:** Web browsing, research, online work

---

### 📊 **Presentation Mode**
- **Active when:** PowerPoint (PPTX, PPT) is open
- **Gesture behavior:**
  - Swipe left → Previous slide
  - Swipe right → Next slide
  - 3-finger swipe → Navigate slides
- **Voice shortcuts:** Optimized for presentation
- **Use for:** Giving presentations, slide navigation

---

### ✍️ **Writing Mode**
- **Active when:** Word, Notepad, or text editors are open
- **Gesture behavior:**
  - Swipe up → Redo last action
  - Swipe down → Undo last action
- **Special features:** Enhanced text editing shortcuts
- **Use for:** Writing documents, coding, text editing

---

### 🎮 **Manual Profile Override**

Force a specific profile using voice commands (even if the app isn't open):

```
"presentation mode"      → Switch to Presentation Profile
"browser mode"           → Switch to Browser Profile
"writing mode"           → Switch to Writing Mode
"default mode"           → Return to Default Mode
```

**Example workflow:**
1. Say "presentation mode"
2. Now all swipes are optimized for presentations, even in other apps
3. Say "default mode" to return to auto-detection

---

## 💬 Dictation Mode

Convert speech to text automatically. Perfect for hands-free typing!

### Enable Dictation
```
"start dictation"        → Enable dictation mode
```

Once enabled:
- Any spoken words are **automatically typed** as text
- Voice commands for actions (copy, paste, etc.) still work
- Dictation appears in the overlay as **"Dictation: ON"**

**Example workflow:**
```
Say: "start dictation"
      → Dictation mode enabled

Say: "Hello world, this is touchless control"
      → Text typed: "Hello world, this is touchless control "

Say: "bold"
      → Text is bolded, dictation continues

Say: "stop dictation"
      → Dictation mode disabled
```

### Disable Dictation
```
"stop dictation"         → Disable dictation mode
```

---

## 📊 Camera Overlay Status

The camera window shows real-time information:

```
┌────────────────────────────────┐
│ Profile: [presentation      ]  │ ← Current active profile
│ Dictation: [ON/OFF          ]  │ ← Dictation mode status
│ Gesture: [none              ]  │ ← Last detected gesture
│ Voice: [                    ]  │ ← Last voice command
│ FPS: 30.1                      │ ← System performance
└────────────────────────────────┘
     [Yellow hand landmarks] 
     [Camera feed]
```

**What to look for:**
- **Profile:** Shows which mode is active (auto-detected or manually set)
- **Dictation:** ON = speaking will type; OFF = normal mode
- **Gesture:** Shows what gesture the system recognized
- **FPS:** Should be 25-30 for smooth operation

---

## 🔧 Settings & Configuration

### Dashboard Settings
The dashboard (separate window) provides access to:
- **Enable/Disable gestures**
- **Enable/Disable voice commands**
- **Microphone selection**
- **Camera selection**
- **Application status**

### Keyboard Shortcuts (while camera window is active)
- **Q** - Quit application
- **R** - Reset gesture detection
- **D** - Toggle debug mode (shows extra info)

---

## 💡 Tips & Best Practices

### For Accurate Gesture Recognition

1. **Lighting is Key**
   - Use good natural or artificial lighting
   - Avoid harsh shadows on hands
   - Don't sit with sun behind you (backlighting)

2. **Hand Position**
   - Keep both hands in frame
   - Position hands 12-24 inches from camera
   - Use camera at eye level for best results

3. **Camera Angle**
   - Position camera slightly above your hand level
   - 30-45 degree downward angle works best
   - Avoid extreme angles

4. **Hand Visibility**
   - Avoid dark clothing that blends with background
   - Wear contrasting colors if possible
   - Remove rings/watches if they interfere

### For Clear Voice Recognition

1. **Speak Clearly**
   - Say commands at normal conversation volume
   - Avoid mumbling or rushing words
   - Pause between commands (1 second)

2. **Background Noise**
   - Minimize background music/TV
   - Quiet fan, keyboard clicking, etc.
   - Microsoft has good voice isolation features

3. **Microphone Setup**
   - Use a quality microphone (laptop mic often works)
   - Position 6-12 inches from your mouth
   - Test through Windows Settings → Sound → Input

4. **Natural Phrases**
   - Say commands naturally ("next slide" not "next... slide")
   - Avoid emphasizing words unnaturally
   - Quick, confident delivery works best

---

## ⚠️ Troubleshooting

### Gestures Not Detected?

**Problem:** Hand landmarks appear but gestures don't work

**Solutions:**
1. Check **lighting** (ensure hands are well-lit)
2. Verify **hand position** (keep in center of frame)
3. Try **larger hand movements** for swipes/clicks
4. Check **FPS** in overlay (should be 25+)
5. Restart application if frozen

### Microphone Not Working?

**Problem:** Voice commands not being recognized

**Solutions:**
1. Check **microphone permission** in Windows Settings
2. Verify **microphone is selected** in dashboard
3. Test microphone with Windows Sound settings
4. Close other audio apps (Zoom, Teams, etc.)
5. Try speaking **louder and more clearly**

### Voice Commands Typing Instead of Executing?

**Problem:** When saying "copy", it types "copy" instead of copying

**Solutions:**
1. Check if **Dictation Mode is ON** (see overlay)
2. Say "stop dictation" to disable
3. Voice commands should work again after disabling

### Camera/Microphone Permission Issues?

**Problem:** "Permission Denied" errors on startup

**Solutions:**
```powershell
# Run as Administrator
1. Right-click run.bat → "Run as Administrator"
2. Or run: python main.py (as admin)
```

Then check Windows Settings → Privacy & Security:
- Camera → Turn ON for Python
- Microphone → Turn ON for Python

### Low FPS (Jerky Cursor)?

**Problem:** System feels slow or cursor is jumpy

**Solutions:**
1. Close **unnecessary applications** (browser tabs, Discord, etc.)
2. Reduce **camera resolution** in config.py (experimental)
3. Update **GPU drivers** for better performance
4. Check for **malware/viruses** consuming CPU
5. Ensure **good ventilation** (prevent CPU throttling)

### Application Crashes?

**Problem:** System crashes or freezes during use

**Solutions:**
```powershell
# Check for errors in console
python main.py > debug.txt 2>&1

# Look for specific error messages in debug.txt

# Common issues:
# - PyAudio not installed properly
# - Microphone not accessible
# - Camera driver issue
```

Try reinstalling dependencies:
```powershell
pip install --upgrade -r requirements.txt
```

---

## 🔄 Workflow Examples

### Example 1: Presenting a PowerPoint

```
1. Say "presentation mode"
   → Profile switches to Presentation Mode
   → Overlay shows "Profile: presentation"

2. Click PowerPoint window to focus
   → System auto-detects presentation mode

3. Say "start presentation"
   → PowerPoint starts fullscreen slideshow

4. Swipe RIGHT
   → Next slide appears

5. Swipe LEFT
   → Previous slide appears

6. Say "go to slide 5"
   → Jumps to slide 5

7. Say "end presentation"
   → Returns to editing view

8. Say "default mode"
   → Return to normal profile
```

### Example 2: Writing a Document with Dictation

```
1. Open Word or Notepad
   → System auto-detects Writing Mode
   → Overlay shows "Profile: writing"

2. Say "start dictation"
   → Overlay shows "Dictation: ON"

3. Say "Hello, this is a test document"
   → Text appears: "Hello, this is a test document "

4. Say "bold"
   → Selected text becomes bold

5. Say "undo undo undo"
   → Last 3 actions are undone

6. Say "stop dictation"
   → Dictation stops, normal mode resumes

7. Say "save document"
   → Document saved
```

### Example 3: Browsing the Web

```
1. Open Chrome
   → System auto-detects Browser Mode
   → Overlay shows "Profile: browser"

2. Point at URL bar, click (index + thumb touch)
   → URL bar selected

3. Say "start dictation"
   → Type website name through dictation

4. Say "stop dictation"
   → Dictation stops

5. Swipe RIGHT
   → Browser goes forward

6. Swipe LEFT
   → Browser goes back

7. Use 2-finger scroll up/down
   → Scroll web page
```

---

## 📱 Performance Tips

- **Close unnecessary applications** before starting
- **Disable antivirus scanning** while using (temporarily safe if trusted)
- **Use external USB camera** for better reliability than built-in
- **Keep Python updated** for performance improvements
- **Update MediaPipe** library periodically for fixes

---

## 🆘 Getting Help

1. **Check overlay status** - shows what system detected
2. **Enable debug mode** - see detailed recognition info
3. **Check console output** - error messages appear here
4. **Test components separately:**
   - Just gestures (disable voice)
   - Just voice (disable gestures)
5. **Restart application** - often fixes temporary glitches

---

## 🎓 Learning Path

**Day 1:** Get comfortable with cursor movement and clicking
```
- Point with index finger
- Practice clicking (index + thumb)
- Get smooth cursor control
```

**Day 2:** Add scrolling and dragging
```
- Practice 2-finger gestures
- Learn drag-and-drop
- Apply to real tasks
```

**Day 3:** Enable voice commands
```
- Learn 5-10 common commands
- Practice dictation mode
- Combine with gestures
```

**Day 4+:** Master profiles and advanced gestures
```
- Switch profiles by word
- Use two-hand gestures
- Optimize workflow
```

---

## 📝 Quick Reference Card

| Action | Gesture/Command | Profile |
|--------|-----------------|---------|
| Move cursor | Point index finger | All |
| Left click | Index + thumb touch | All |
| Drag | Pinch + hold | All |
| Scroll | 2-finger up/down | All |
| Next slide | Swipe right | Presentation |
| Prev slide | Swipe left | Presentation |
| Volume up | Thumb up | All |
| Dictation | "Start dictation" | All |
| Lock screen | Both palms out | All |
| Zoom | Hands spread/close | All |

---

## 🚀 Bonus Tips

- **Rest your hands** - gestures use arm muscles
- **Take breaks** - every 30-45 minutes look away from screen
- **Adjust camera height** - match your natural hand position
- **Practice in mirrors** - see what camera sees
- **Record yourself** - improve gesture quality
- **Join community** - share tips with other users

---

**Happy gesturing! 🖐️✨**

For technical support or feature requests, check the project documentation.
