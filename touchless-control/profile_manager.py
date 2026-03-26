"""
Active-window profile manager for app-aware behavior.
"""

import ctypes


class ProfileManager:
    """Detect and manage profile selection based on active window title."""

    def __init__(self):
        self.current_profile = "default"
        self.manual_profile = None

    def set_manual_profile(self, profile_name):
        """Force profile selection until cleared."""
        self.manual_profile = profile_name
        self.current_profile = profile_name

    def clear_manual_profile(self):
        """Return to auto profile detection."""
        self.manual_profile = None

    def get_active_window_title(self):
        """Read the active window title on Windows."""
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""

        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value or ""

    def detect_profile(self, window_title):
        """Map current window title to a profile name."""
        title = (window_title or "").lower()

        if any(key in title for key in ["powerpoint", ".ppt", "slide show"]):
            return "presentation"
        if any(key in title for key in ["chrome", "firefox", "edge", "browser"]):
            return "browser"
        if any(key in title for key in ["word", "notepad", "editor", "document"]):
            return "writing"
        return "default"

    def update_active_profile(self):
        """Refresh profile from active window unless manually pinned."""
        if self.manual_profile:
            return self.current_profile

        title = self.get_active_window_title()
        self.current_profile = self.detect_profile(title)
        return self.current_profile

    def get_profile(self):
        """Return the currently selected profile name."""
        return self.current_profile
