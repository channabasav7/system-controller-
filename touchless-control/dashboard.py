"""
GUI dashboard using Tkinter.

Provides a simple interface for:
- Starting/stopping the system
- Enabling/disabling voice control
- Adjusting sensitivity settings
- Viewing system status
"""

import tkinter as tk
from tkinter import ttk
import config


class Dashboard:
    """
    Tkinter-based GUI dashboard for the touchless control system.
    """

    def __init__(self, start_callback, stop_callback, voice_toggle_callback):
        """
        Initialize the dashboard.

        Args:
            start_callback: function to call when Start button is pressed
            stop_callback: function to call when Stop button is pressed
            voice_toggle_callback: function to call when voice control is toggled
        """
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.voice_toggle_callback = voice_toggle_callback

        self.root = tk.Tk()
        self.root.title("Touchless Control Dashboard")
        self.root.geometry(f"{config.DASHBOARD_WIDTH}x{config.DASHBOARD_HEIGHT}")
        self.root.resizable(False, False)

        self.running = False
        self.voice_enabled = False
        self.control_mode = tk.StringVar(value="hand")

        self._create_widgets()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # ────────────── Header ──────────────────────────────────────────────
        header_frame = tk.Frame(self.root, bg="#2C3E50", height=80)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="🖐️ Touchless Laptop Control",
            font=("Arial", 18, "bold"),
            bg="#2C3E50",
            fg="white"
        )
        title_label.pack(pady=20)

        # ────────────── Control Buttons ─────────────────────────────────────
        control_frame = tk.Frame(self.root, padx=20, pady=20)
        control_frame.pack(fill=tk.BOTH, expand=True)

        # Start/Stop button
        self.start_button = tk.Button(
            control_frame,
            text="▶ Start System",
            font=("Arial", 14, "bold"),
            bg="#27AE60",
            fg="white",
            width=20,
            height=2,
            command=self._on_start
        )
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(
            control_frame,
            text="⏹ Stop System",
            font=("Arial", 14, "bold"),
            bg="#E74C3C",
            fg="white",
            width=20,
            height=2,
            command=self._on_stop,
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=10)

        # ────────────── Control Mode ────────────────────────────────────────
        mode_frame = tk.LabelFrame(
            control_frame,
            text="Control Mode",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        mode_frame.pack(pady=10, fill=tk.X)

        tk.Radiobutton(
            mode_frame,
            text="Hand Gesture",
            variable=self.control_mode,
            value="hand",
            font=("Arial", 11)
        ).pack(anchor=tk.W)

        tk.Radiobutton(
            mode_frame,
            text="Iris Eye Tracking",
            variable=self.control_mode,
            value="iris",
            font=("Arial", 11)
        ).pack(anchor=tk.W)

        # ────────────── Voice Control Toggle ────────────────────────────────
        voice_frame = tk.LabelFrame(
            control_frame,
            text="Voice Control",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        voice_frame.pack(pady=20, fill=tk.X)

        self.voice_check = tk.Checkbutton(
            voice_frame,
            text="Enable Voice Commands",
            font=("Arial", 11),
            variable=tk.BooleanVar(),
            command=self._on_voice_toggle
        )
        self.voice_check.pack()

        # ────────────── Status Display ──────────────────────────────────────
        status_frame = tk.LabelFrame(
            control_frame,
            text="Status",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        status_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        self.status_text = tk.Text(
            status_frame,
            height=8,
            width=45,
            font=("Courier", 9),
            state=tk.DISABLED,
            bg="#ECF0F1"
        )
        self.status_text.pack()

        self._update_status("Ready to start")

        # ────────────── Settings (Optional) ─────────────────────────────────
        settings_frame = tk.LabelFrame(
            control_frame,
            text="Sensitivity",
            font=("Arial", 12, "bold"),
            padx=10,
            pady=10
        )
        settings_frame.pack(pady=10, fill=tk.X)

        tk.Label(settings_frame, text="Cursor Smoothing:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.smoothing_scale = tk.Scale(
            settings_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            length=200
        )
        self.smoothing_scale.set(int(config.SMOOTHING_FACTOR * 100))
        self.smoothing_scale.grid(row=0, column=1, pady=5)

        # ────────────── Footer ──────────────────────────────────────────────
        footer_label = tk.Label(
            self.root,
            text="Press 'q' in video window to quit | Made with Python 🐍",
            font=("Arial", 8),
            fg="gray"
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)

    def _on_start(self):
        """Handle Start button click."""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self._update_status(f"System started ({self.control_mode.get()} mode)")
        if self.start_callback:
            self.start_callback(self.control_mode.get())

    def _on_stop(self):
        """Handle Stop button click."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self._update_status("System stopped")
        if self.stop_callback:
            self.stop_callback()

    def _on_voice_toggle(self):
        """Handle voice control toggle."""
        self.voice_enabled = not self.voice_enabled
        status = "enabled" if self.voice_enabled else "disabled"
        self._update_status(f"Voice control {status}")
        if self.voice_toggle_callback:
            self.voice_toggle_callback(self.voice_enabled)

    def _update_status(self, message):
        """
        Update the status text display.

        Args:
            message: str, status message to display
        """
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"> {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def update_gesture_status(self, gesture):
        """
        Update status with current gesture.

        Args:
            gesture: str, detected gesture
        """
        if gesture != config.GESTURE_NONE:
            self._update_status(f"Gesture: {gesture}")

    def get_smoothing_factor(self):
        """
        Get current smoothing factor from slider.

        Returns:
            float: smoothing factor (0-1)
        """
        return self.smoothing_scale.get() / 100.0

    def run(self):
        """Start the Tkinter main loop."""
        self.root.mainloop()

    def close(self):
        """Close the dashboard window."""
        self.root.quit()
        self.root.destroy()
