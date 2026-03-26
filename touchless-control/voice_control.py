"""
Voice control module using SpeechRecognition and PyAudio.

Listens for voice commands in a separate thread and maps them
to actions via the MouseController and PresentationController.
"""

import re
import threading
import speech_recognition as sr
import config


class VoiceController:
    """
    Handles voice recognition and command processing.
    """

    def __init__(self, mouse_controller, presentation_controller, profile_manager=None):
        """
        Initialize voice controller.

        Args:
            mouse_controller: MouseController instance
            presentation_controller: PresentationController instance
        """
        self.mouse_controller = mouse_controller
        self.presentation_controller = presentation_controller
        self.profile_manager = profile_manager

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.VOICE_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = config.VOICE_PAUSE_THRESHOLD

        self.microphone = sr.Microphone()

        self.listening = False
        self.thread = None
        self.dictation_mode = False

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

                    # Process command; if not handled and dictation is on, type the text.
                    handled = self._process_command(text)
                    if not handled and self.dictation_mode:
                        self.mouse_controller.type_text(text + " ")
                        self.last_command = f"dictation: {text}"

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
        # Check if text matches any voice command.
        # Longer phrases first avoid shorter generic matches stealing intent.
        command = None
        for phrase in sorted(config.VOICE_COMMANDS, key=len, reverse=True):
            cmd = config.VOICE_COMMANDS[phrase]
            if phrase in text:
                command = cmd
                break

        if not command:
            return False

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
            elif command == "go_to_slide":
                slide_number = self._extract_slide_number(text)
                if slide_number is not None:
                    self.presentation_controller.go_to_slide(slide_number)
                else:
                    print("[Voice] Slide number not found in command")
                    return
            elif command == "black_screen":
                self.presentation_controller.toggle_blackout()
            elif command == "scroll_down":
                self.mouse_controller.scroll_down()
            elif command == "scroll_up":
                self.mouse_controller.scroll_up()
            elif command == "zoom_in":
                self.mouse_controller.zoom_in()
            elif command == "zoom_out":
                self.mouse_controller.zoom_out()
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
            elif command == "volume_up":
                self.mouse_controller.volume_up()
            elif command == "volume_down":
                self.mouse_controller.volume_down()
            elif command == "mute_audio":
                self.mouse_controller.mute_audio()
            elif command == "lock_screen":
                self.mouse_controller.lock_screen()
            elif command == "switch_window":
                self.mouse_controller.switch_window()
            elif command == "open_task_manager":
                self.mouse_controller.open_task_manager()
            elif command == "copy":
                self.mouse_controller.copy()
            elif command == "paste":
                self.mouse_controller.paste()
            elif command == "select_all":
                self.mouse_controller.select_all()
            elif command == "undo":
                self.mouse_controller.undo()
            elif command == "redo":
                self.mouse_controller.redo()
            elif command == "bold":
                self.mouse_controller.bold()
            elif command == "italic":
                self.mouse_controller.italic()
            elif command == "underline":
                self.mouse_controller.underline()
            elif command == "align_left":
                self.mouse_controller.align_left()
            elif command == "center_align":
                self.mouse_controller.center_align()
            elif command == "save_document":
                self.mouse_controller.save_document()
            elif command == "new_paragraph":
                self.mouse_controller.new_paragraph()
            elif command == "start_dictation":
                self.dictation_mode = True
                print("[Voice] Dictation mode enabled")
            elif command == "stop_dictation":
                self.dictation_mode = False
                print("[Voice] Dictation mode disabled")
            elif command == "set_profile_presentation":
                if self.profile_manager:
                    self.profile_manager.set_manual_profile("presentation")
                    print("[Voice] Profile set to presentation")
            elif command == "set_profile_browser":
                if self.profile_manager:
                    self.profile_manager.set_manual_profile("browser")
                    print("[Voice] Profile set to browser")
            elif command == "set_profile_writing":
                if self.profile_manager:
                    self.profile_manager.set_manual_profile("writing")
                    print("[Voice] Profile set to writing")
            elif command == "set_profile_default":
                if self.profile_manager:
                    self.profile_manager.clear_manual_profile()
                    self.profile_manager.update_active_profile()
                    print("[Voice] Profile reset to auto/default")
            else:
                print(f"[Voice] Unknown command: {command}")
                return False

            print(f"[Voice] Executed: {command}")
            return True
        except Exception as e:
            print(f"[Voice] Error executing command '{command}': {e}")
            return False

    def get_last_command(self):
        """
        Get the last recognized command text.

        Returns:
            str: last command text
        """
        return self.last_command

    def _extract_slide_number(self, text):
        """Extract a slide number from recognized text."""
        match = re.search(r"\b(?:go to slide\s+)?(\d{1,4})\b", text)
        if match:
            return int(match.group(1))
        return None
