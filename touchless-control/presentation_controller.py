"""
PowerPoint presentation control module.

Handles presentation‑specific commands like next/previous slide,
starting/stopping slideshow mode.
"""

import pyautogui


class PresentationController:
    """
    Controls PowerPoint presentations.
    """

    def __init__(self):
        """Initialize presentation state."""
        self.presentation_mode = False

    def start_presentation(self):
        """Start slideshow from the beginning (F5 in PowerPoint)."""
        pyautogui.press("F5")
        self.presentation_mode = True
        print("[Presentation] Started slideshow")

    def stop_presentation(self):
        """Exit slideshow (Esc key)."""
        pyautogui.press("esc")
        self.presentation_mode = False
        print("[Presentation] Stopped slideshow")

    def next_slide(self):
        """Go to next slide (Right arrow or Page Down)."""
        pyautogui.press("right")

    def previous_slide(self):
        """Go to previous slide (Left arrow or Page Up)."""
        pyautogui.press("left")

    def go_to_slide(self, slide_number):
        """Jump to a specific slide number in slideshow mode."""
        if slide_number <= 0:
            return
        pyautogui.typewrite(str(slide_number))
        pyautogui.press("enter")

    def toggle_blackout(self):
        """Toggle screen blackout (B key in PowerPoint)."""
        pyautogui.press("b")

    def toggle_whiteboard(self):
        """Toggle whiteboard (W key in PowerPoint)."""
        pyautogui.press("w")

    def laser_pointer(self):
        """
        Enable laser pointer mode (Ctrl+L in PowerPoint).
        
        Note: Actual laser pointer effect requires PowerPoint-specific integration.
        This is a placeholder for advanced functionality.
        """
        pyautogui.hotkey("ctrl", "l")
