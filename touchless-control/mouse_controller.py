"""
Mouse and keyboard control module using PyAutoGUI.

Provides high‑level wrappers for cursor movement, clicks, scrolling,
and keyboard shortcuts.
"""

import pyautogui
import subprocess
import config

# Fail‑safe: move mouse to top‑left corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.01


class MouseController:
    """
    Handles all mouse and keyboard actions.
    """

    def __init__(self):
        """Initialize controller state."""
        self.drag_mode = False

    def move_cursor(self, x, y):
        """
        Move mouse cursor to (x, y) screen coordinates.

        Args:
            x: int, x‑coordinate
            y: int, y‑coordinate
        """
        pyautogui.moveTo(x, y, duration=0)

    def left_click(self):
        """Perform a left mouse click."""
        pyautogui.click()

    def right_click(self):
        """Perform a right mouse click."""
        pyautogui.rightClick()

    def start_drag(self):
        """Start drag mode by pressing down left mouse button."""
        if not self.drag_mode:
            pyautogui.mouseDown()
            self.drag_mode = True

    def end_drag(self):
        """End drag mode by releasing left mouse button."""
        if self.drag_mode:
            pyautogui.mouseUp()
            self.drag_mode = False

    def scroll_up(self, clicks=None):
        """
        Scroll up.

        Args:
            clicks: int, number of scroll clicks (default from config)
        """
        if clicks is None:
            clicks = config.SCROLL_SPEED
        pyautogui.scroll(clicks)

    def scroll_down(self, clicks=None):
        """
        Scroll down.

        Args:
            clicks: int, number of scroll clicks (default from config)
        """
        if clicks is None:
            clicks = config.SCROLL_SPEED
        pyautogui.scroll(-clicks)

    def press_key(self, key):
        """
        Press a single key.

        Args:
            key: str, key name (e.g., 'enter', 'space', 'esc')
        """
        pyautogui.press(key)

    def hotkey(self, *keys):
        """
        Press a combination of keys.

        Args:
            *keys: sequence of key names (e.g., 'ctrl', 'c')
        """
        pyautogui.hotkey(*keys)

    def open_application(self, app_name):
        """
        Open an application on Windows.

        Args:
            app_name: str, name of the application
        """
        try:
            if app_name.lower() == "chrome":
                subprocess.Popen(["start", "chrome"], shell=True)
            elif app_name.lower() == "powerpoint":
                subprocess.Popen(["start", "powerpnt"], shell=True)
            elif app_name.lower() == "notepad":
                subprocess.Popen(["notepad.exe"])
            elif app_name.lower() == "calculator":
                subprocess.Popen(["calc.exe"])
            else:
                # Try to start by name
                subprocess.Popen(["start", app_name], shell=True)
        except Exception as e:
            print(f"[MouseController] Failed to open {app_name}: {e}")

    def close_window(self):
        """Close the active window (Alt+F4)."""
        self.hotkey("alt", "F4")

    def minimize_window(self):
        """Minimize the active window (Win+Down)."""
        self.hotkey("win", "down")

    def maximize_window(self):
        """Maximize the active window (Win+Up)."""
        self.hotkey("win", "up")

    def take_screenshot(self):
        """Take a screenshot (Win+Shift+S on Windows 10/11)."""
        self.hotkey("win", "shift", "s")
