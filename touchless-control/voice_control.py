"""
Voice control module using SpeechRecognition and PyAudio.

Listens for voice commands in a separate thread and maps them
to actions via the MouseController and PresentationController.
"""

import threading
import speech_recognition as sr
import config


class VoiceController:
    """
    Handles voice recognition and command processing.
    """

    def __init__(self, mouse_controller, presentation_controller):
        """
        Initialize voice controller.

        Args:
            mouse_controller: MouseController instance
            presentation_controller: PresentationController instance
        """
        self.mouse_controller = mouse_controller
        self.presentation_controller = presentation_controller

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.VOICE_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = config.VOICE_PAUSE_THRESHOLD

        self.microphone = sr.Microphone()

        self.listening = False
        self.thread = None

        self.last_command = ""

    def start_listening(self):
        """Start voice recognition in a background thread."""
        if not self.listening:
            self.listening = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print("[Voice] Started listening")

    def stop_listening(self):
        """Stop voice recognition thread."""
        self.listening = False
        if self.thread:
            self.thread.join(timeout=2)
        print("[Voice] Stopped listening")

    def _listen_loop(self):
        """Main voice recognition loop (runs in separate thread)."""
        with self.microphone as source:
            # Adjust for ambient noise once at startup
            print("[Voice] Calibrating for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[Voice] Calibration complete. Listening for commands...")

            while self.listening:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(
                        source,
                        timeout=config.VOICE_TIMEOUT,
                        phrase_time_limit=5
                    )

                    # Recognize speech using Google Speech Recognition
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"[Voice] Heard: '{text}'")

                    # Process command
                    self._process_command(text)

                except sr.WaitTimeoutError:
                    # No speech detected within timeout
                    pass
                except sr.UnknownValueError:
                    # Speech not understood
                    print("[Voice] Could not understand audio")
                except sr.RequestError as e:
                    # API error
                    print(f"[Voice] API error: {e}")
                except Exception as e:
                    print(f"[Voice] Unexpected error: {e}")

    def _process_command(self, text):
        """
        Process recognized text and execute corresponding action.

        Args:
            text: str, recognized speech in lowercase
        """
        # Check if text matches any voice command
        command = None
        for phrase, cmd in config.VOICE_COMMANDS.items():
            if phrase in text:
                command = cmd
                break

        if not command:
            return

        self.last_command = text

        # Execute command
        try:
            if command == "open_chrome":
                self.mouse_controller.open_application("chrome")
            elif command == "open_powerpoint":
                self.mouse_controller.open_application("powerpoint")
            elif command == "next_slide":
                self.presentation_controller.next_slide()
            elif command == "previous_slide":
                self.presentation_controller.previous_slide()
            elif command == "scroll_down":
                self.mouse_controller.scroll_down()
            elif command == "scroll_up":
                self.mouse_controller.scroll_up()
            elif command == "close_window":
                self.mouse_controller.close_window()
            elif command == "start_presentation":
                self.presentation_controller.start_presentation()
            elif command == "stop_presentation":
                self.presentation_controller.stop_presentation()
            elif command == "minimize_window":
                self.mouse_controller.minimize_window()
            elif command == "maximize_window":
                self.mouse_controller.maximize_window()
            elif command == "open_notepad":
                self.mouse_controller.open_application("notepad")
            elif command == "open_calculator":
                self.mouse_controller.open_application("calculator")
            elif command == "take_screenshot":
                self.mouse_controller.take_screenshot()
            else:
                print(f"[Voice] Unknown command: {command}")

            print(f"[Voice] Executed: {command}")
        except Exception as e:
            print(f"[Voice] Error executing command '{command}': {e}")

    def get_last_command(self):
        """
        Get the last recognized command text.

        Returns:
            str: last command text
        """
        return self.last_command
