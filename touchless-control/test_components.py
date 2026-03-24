#!/usr/bin/env python3
"""
Test script to verify camera and audio components.
Run this to diagnose issues before starting the main application.
"""

import cv2
import sys
import os

def test_camera():
    """Test camera access and list available cameras."""
    print("\n" + "="*50)
    print("CAMERA TEST")
    print("="*50)
    
    available_cameras = []
    
    # Test camera indices 0-5
    for i in range(6):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available_cameras.append(i)
                print(f"  [OK] Camera {i}: Available")
            else:
                print(f"  [WARN] Camera {i}: Opened but can't read frame")
            cap.release()
        else:
            print(f"  [--] Camera {i}: Not available")
    
    if available_cameras:
        print(f"\n  Available cameras: {available_cameras}")
        print(f"  Recommended: Use CAMERA_INDEX = {available_cameras[0]} in config.py")
        return True
    else:
        print("\n  [ERROR] No cameras found!")
        print("  Solutions:")
        print("  1. Check if webcam is connected")
        print("  2. Close other apps using camera (Zoom, Teams, etc.)")
        print("  3. Check Windows Privacy settings > Camera access")
        return False

def test_mediapipe():
    """Test MediaPipe installation and model file."""
    print("\n" + "="*50)
    print("MEDIAPIPE TEST")
    print("="*50)
    
    try:
        import mediapipe as mp
        print(f"  [OK] MediaPipe version: {mp.__version__}")
        
        # Check for model file
        model_path = 'hand_landmarker.task'
        if os.path.exists(model_path):
            size_mb = os.path.getsize(model_path) / (1024*1024)
            print(f"  [OK] Hand landmarker model found ({size_mb:.1f} MB)")
            return True
        else:
            print(f"  [ERROR] Model file not found: {model_path}")
            print("  Download from: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task")
            return False
    except ImportError as e:
        print(f"  [ERROR] MediaPipe not installed: {e}")
        print("  Run: pip install mediapipe")
        return False

def test_audio():
    """Test audio/microphone access."""
    print("\n" + "="*50)
    print("AUDIO TEST")
    print("="*50)
    
    try:
        import speech_recognition as sr
        print(f"  [OK] SpeechRecognition installed")
        
        r = sr.Recognizer()
        mics = sr.Microphone.list_microphone_names()
        
        if mics:
             print(f"  [OK] Found {len(mics)} microphone(s):")
             for index, name in enumerate(mics[:5]):

                print(f"      {index}: {name}")

        else:
            print("  [WARN] No microphones found")
        
        # Test PyAudio
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            print(f"  [OK] PyAudio working")
            p.terminate()
            return True
        except Exception as e:
            print(f"  [ERROR] PyAudio issue: {e}")
            print("  Fix: See PyAudio installation instructions below")
            return False
            
    except ImportError as e:
        print(f"  [ERROR] SpeechRecognition not installed: {e}")
        return False

def test_pyautogui():
    """Test PyAutoGUI for mouse control."""
    print("\n" + "="*50)
    print("PYAUTOGUI TEST")
    print("="*50)
    
    try:
        import pyautogui
        size = pyautogui.size()
        print(f"  [OK] Screen size: {size}")
        print(f"  [OK] PyAutoGUI ready")
        return True
    except Exception as e:
        print(f"  [ERROR] PyAutoGUI error: {e}")
        return False

def test_imports():
    """Test all project module imports."""
    print("\n" + "="*50)
    print("MODULE IMPORTS TEST")
    print("="*50)
    
    modules = ['config', 'gesture_control', 'mouse_controller', 
               'voice_control', 'display', 'dashboard', 'utils', 
               'presentation_controller']
    
    all_ok = True
    for mod in modules:
        try:
            __import__(mod)
            print(f"  [OK] {mod}")
        except Exception as e:
            print(f"  [ERROR] {mod}: {e}")
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*60)
    print("  TOUCHLESS CONTROL - COMPONENT DIAGNOSTIC")
    print("="*60)
    
    results = {
        'Camera': test_camera(),
        'MediaPipe': test_mediapipe(),
        'Audio': test_audio(),
        'PyAutoGUI': test_pyautogui(),
        'Imports': test_imports()
    }
    
    print("\n" + "="*60)
    print("  SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n  All components working! Run: python main.py")
    else:
        print("\n  Some components need fixing. See details above.")
    
    print("="*60)
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)