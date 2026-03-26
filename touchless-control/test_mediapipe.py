#!/usr/bin/env python3
"""Test MediaPipe installation and available attributes."""

import sys

try:
    import mediapipe as mp
    print(f"✓ MediaPipe imported successfully")
    print(f"✓ Version: {mp.__version__}")
    print(f"✓ Has 'solutions': {hasattr(mp, 'solutions')}")
    
    if hasattr(mp, 'solutions'):
        print(f"✓ Has 'solutions.face_mesh': {hasattr(mp.solutions, 'face_mesh')}")
    else:
        print("✗ 'solutions' module not found")
        print(f"Available attributes: {dir(mp)}")
        
except ImportError as e:
    print(f"✗ MediaPipe not installed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
