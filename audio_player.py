
import time
from pathlib import Path

import pygame
from mutagen.mp3 import MP3


class AudioPlayer:
    """
    Nova TTS Audio Player

    Features:
        - Play
        - Pause
        - Resume
        - Stop
        - Seek
        - Volume control
        - MP3 duration detection
    """

    def __init__(self):

        if not pygame.mixer.get_init():
            pygame.mixer.init()

        self.file_path = None

        self.duration = 0.0
        self.position = 0.0

        self.state = "stopped"

        self._started_at = 0.0
        self._volume = 0.8

        pygame.mixer.music.set_volume(
            self._volume
        )

    # ----------------------------------
    # LOAD AUDIO
    # ----------------------------------

    def load_file(self, file_path):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {path}"
            )

        if path.suffix.lower() != ".mp3":
            raise ValueError(
                "Only MP3 files are supported."
            )

        # Read audio duration
        audio = MP3(str(path))

        duration = float(audio.info.length)

        if duration <= 0:
            raise ValueError(
                "Invalid audio duration."
            )

        # Stop previous audio
        pygame.mixer.music.stop()

        # Load new audio
        pygame.mixer.music.load(
            str(path)
        )

        pygame.mixer.music.set_volume(self._volume)

        self.file_path = path

        self.duration = duration

        self.position = 0.0

        self.state = "stopped"

    # ----------------------------------
    # PLAY
    # ----------------------------------

    def play(self):

        if self.file_path is None:
            raise RuntimeError(
                "No audio file loaded."
            )

        if self.state == "playing":
            return

        # Resume if paused
        if self.state == "paused":

            self.resume()
            return

        # Restart if finished
        if self.position >= self.duration:

            self.position = 0.0

        start_position = self.position

        pygame.mixer.music.play(
            start=start_position
        )

        self.position = start_position

        self._started_at = time.monotonic()

        self.state = "playing"

    # ----------------------------------
    # PAUSE
    # ----------------------------------

    def pause(self):

        if self.state != "playing":
            return

        current_position = self.get_position()

        pygame.mixer.music.pause()

        self.position = current_position

        self.state = "paused"

    # ----------------------------------
    # RESUME
    # ----------------------------------

    def resume(self):

        if self.state != "paused":
            return

        pygame.mixer.music.unpause()

        self._started_at = time.monotonic()

        self.state = "playing"

    # ----------------------------------
    # STOP
    # ----------------------------------

    def stop(self):

        pygame.mixer.music.stop()

        self.position = 0.0

        self.state = "stopped"

    # ----------------------------------
    # SEEK
    # ----------------------------------

    def seek(self, seconds):

        if self.file_path is None:
            return

        target = max(
            0.0,
            min(float(seconds), self.duration)
        )

        if target >= self.duration:

            self.stop()

            self.position = self.duration

            return

        previous_state = self.state

        # No playback needed when stopped
        if previous_state == "stopped":

            self.position = target

            return

        # Restart playback from target position
        pygame.mixer.music.play(
            start=target
        )

        self.position = target

        self._started_at = time.monotonic()

        if previous_state == "paused":

            pygame.mixer.music.pause()

            self.state = "paused"

        else:

            self.state = "playing"

    # ----------------------------------
    # GET POSITION
    # ----------------------------------

    def get_position(self):

        if self.state != "playing":
            return self.position

        elapsed = max(
            0.0,
            time.monotonic() - self._started_at
        )

        current_position = min(
            self.position + elapsed,
            self.duration
        )

        # Detect end of playback
        if current_position >= self.duration:

            pygame.mixer.music.stop()

            self.position = self.duration

            self.state = "stopped"

            return self.position

        # Detect natural playback completion
        if (
            not pygame.mixer.music.get_busy()
            and elapsed > 0.35
        ):

            self.position = self.duration

            self.state = "stopped"

            return self.position

        return current_position

    # ----------------------------------
    # VOLUME
    # ----------------------------------

    def set_volume(self, value):

        self._volume = max(
            0.0,
            min(float(value), 1.0)
        )

        pygame.mixer.music.set_volume(
            self._volume
        )

    # ----------------------------------
    # CLOSE
    # ----------------------------------

    def close(self):

        pygame.mixer.music.stop()

        pygame.mixer.quit()

        self.state = "stopped"
