
import asyncio
import threading
import queue

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from tts_engine import synthesize_text

from voice_manager import (
    fetch_available_voices,
    filter_voices
)

from audio_player import AudioPlayer


# ==========================================
# NOVA TTS - VERSION 3.0
# ==========================================


class NovaTTSApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Nova TTS")
        self.geometry("1150x780")
        self.minsize(900, 650)

        # Application states
        self.is_busy = False
        self.voice_loading = False
        self.closing = False

        # Thread communication
        self.worker_queue = queue.Queue()

        # Voice manager
        self.all_voices = []
        self.voice_map = {}

        # Audio player initialization
        self.audio_player = None
        self.audio_error = None
        self._seek_dragging = False

        try:
            self.audio_player = AudioPlayer()

        except Exception as error:
            self.audio_error = str(error)

        # Theme
        self.current_appearance = "Dark"

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        # Build interface
        self.build_ui()

        # Background message processing
        self.after(
            100,
            self.process_worker_messages
        )

        # Audio player UI updates
        self.after(
            250,
            self.update_audio_ui
        )

        # Load voices
        self.load_voices()

    # ======================================
    # MAIN UI
    # ======================================

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            padx=24,
            pady=(20, 10),
            sticky="ew"
        )

        header.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            header,
            text="Nova TTS",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            header,
            text="Professional Text to Speech Studio",
            text_color="gray"
        ).grid(
            row=1,
            column=0,
            sticky="w"
        )

        self.theme_button = ctk.CTkButton(
            header,
            text="Toggle Theme",
            width=120,
            command=self.toggle_theme
        )

        self.theme_button.grid(
            row=0,
            column=1,
            rowspan=2
        )

        # Main content
        body = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        body.grid(
            row=1,
            column=0,
            padx=24,
            pady=10,
            sticky="nsew"
        )

        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self.build_editor(body)
        self.build_settings(body)

        # Footer
        ctk.CTkLabel(
            self,
            text="Nova TTS | Version 3.0",
            text_color="gray"
        ).grid(
            row=2,
            column=0,
            pady=(5, 15)
        )

    # ======================================
    # TEXT EDITOR
    # ======================================

    def build_editor(self, parent):

        editor = ctk.CTkFrame(
            parent,
            corner_radius=16
        )

        editor.grid(
            row=0,
            column=0,
            padx=(0, 10),
            sticky="nsew"
        )

        editor.grid_columnconfigure(
            0,
            weight=1
        )

        editor.grid_rowconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            editor,
            text="Text Editor",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
            sticky="w"
        )

        # Text input
        self.text_box = ctk.CTkTextbox(
            editor,
            font=ctk.CTkFont(size=15),
            corner_radius=10
        )

        self.text_box.grid(
            row=1,
            column=0,
            padx=20,
            pady=10,
            sticky="nsew"
        )

        self.text_box.bind(
            "<KeyRelease>",
            self.update_counter
        )

        # Bottom section
        bottom = ctk.CTkFrame(
            editor,
            fg_color="transparent"
        )

        bottom.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        bottom.grid_columnconfigure(
            0,
            weight=1
        )

        self.counter_label = ctk.CTkLabel(
            bottom,
            text="0 characters",
            text_color="gray"
        )

        self.counter_label.grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkButton(
            bottom,
            text="Clear Text",
            width=110,
            fg_color="gray",
            command=self.clear_text
        ).grid(
            row=0,
            column=1
        )

        # Audio player
        self.build_audio_player(editor)

    # ======================================
    # AUDIO PLAYER UI
    # ======================================

    def build_audio_player(self, parent):

        player = ctk.CTkFrame(
            parent,
            corner_radius=14
        )

        player.grid(
            row=3,
            column=0,
            padx=15,
            pady=(5, 15),
            sticky="ew"
        )

        player.grid_columnconfigure(
            0,
            weight=1
        )

        # Header
        header = ctk.CTkFrame(
            player,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            padx=15,
            pady=(12, 5),
            sticky="ew"
        )

        header.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            header,
            text="Audio Player",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.audio_file_label = ctk.CTkLabel(
            header,
            text="No file loaded",
            text_color="gray"
        )

        self.audio_file_label.grid(
            row=0,
            column=1,
            padx=10,
            sticky="e"
        )

        # Timeline
        self.seek_slider = ctk.CTkSlider(
            player,
            from_=0,
            to=1000,
            command=self.preview_seek
        )

        self.seek_slider.set(0)

        self.seek_slider.grid(
            row=1,
            column=0,
            padx=18,
            pady=(8, 3),
            sticky="ew"
        )

        self.seek_slider.bind(
            "<ButtonPress-1>",
            self.on_seek_press
        )

        self.seek_slider.bind(
            "<ButtonRelease-1>",
            self.on_seek_release
        )

        # Time label
        self.time_label = ctk.CTkLabel(
            player,
            text="00:00 / 00:00",
            text_color="gray"
        )

        self.time_label.grid(
            row=2,
            column=0,
            padx=18,
            pady=3,
            sticky="e"
        )

        # Playback buttons
        controls = ctk.CTkFrame(
            player,
            fg_color="transparent"
        )

        controls.grid(
            row=3,
            column=0,
            padx=15,
            pady=8,
            sticky="ew"
        )

        self.play_button = ctk.CTkButton(
            controls,
            text="▶ Play",
            width=85,
            command=self.play_audio
        )

        self.play_button.grid(
            row=0,
            column=0,
            padx=3
        )

        self.pause_button = ctk.CTkButton(
            controls,
            text="Ⅱ Pause",
            width=105,
            command=self.toggle_pause,
            fg_color="#555555"
        )

        self.pause_button.grid(
            row=0,
            column=1,
            padx=3
        )

        self.stop_button = ctk.CTkButton(
            controls,
            text="■ Stop",
            width=85,
            command=self.stop_audio,
            fg_color="#9B4242"
        )

        self.stop_button.grid(
            row=0,
            column=2,
            padx=3
        )

        self.open_audio_button = ctk.CTkButton(
            controls,
            text="Open MP3",
            width=100,
            command=self.open_audio_file,
            fg_color="gray"
        )

        self.open_audio_button.grid(
            row=0,
            column=3,
            padx=3
        )

        # Volume
        volume_frame = ctk.CTkFrame(
            player,
            fg_color="transparent"
        )

        volume_frame.grid(
            row=4,
            column=0,
            padx=18,
            pady=(5, 10),
            sticky="ew"
        )

        volume_frame.grid_columnconfigure(
            1,
            weight=1
        )

        ctk.CTkLabel(
            volume_frame,
            text="Volume"
        ).grid(
            row=0,
            column=0,
            padx=(0, 10)
        )

        self.playback_volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0,
            to=100,
            command=self.change_playback_volume
        )

        self.playback_volume_slider.set(80)

        self.playback_volume_slider.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        self.player_status_label = ctk.CTkLabel(
            player,
            text="Ready",
            text_color="gray"
        )

        self.player_status_label.grid(
            row=5,
            column=0,
            padx=15,
            pady=(0, 10)
        )

        # Disable player controls when mixer is unavailable
        self.audio_controls = [
            self.play_button,
            self.pause_button,
            self.stop_button,
            self.seek_slider,
            self.playback_volume_slider,
            self.open_audio_button
        ]

        if self.audio_player is None:

            for widget in self.audio_controls:

                widget.configure(
                    state="disabled"
                )

            self.player_status_label.configure(
                text=f"Audio player unavailable: {self.audio_error}"
            )

        else:

            self.audio_player.set_volume(0.8)

            self.seek_slider.configure(
                state="disabled"
            )

            self.play_button.configure(
                state="disabled"
            )

            self.pause_button.configure(
                state="disabled"
            )

            self.stop_button.configure(
                state="disabled"
            )

    # ======================================
    # AUDIO PLAYER FUNCTIONS
    # ======================================

    def format_time(self, seconds):

        seconds = max(
            0,
            int(seconds)
        )

        minutes = seconds // 60
        remaining = seconds % 60

        hours = minutes // 60
        minutes = minutes % 60

        if hours:

            return (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{remaining:02d}"
            )

        return (
            f"{minutes:02d}:"
            f"{remaining:02d}"
        )

    # --------------------------------------
    # ENABLE / DISABLE CONTROLS
    # --------------------------------------

    def set_audio_controls_enabled(self, enabled):

        if self.audio_player is None:
            return

        state = "normal" if enabled else "disabled"

        for widget in [
            self.play_button,
            self.pause_button,
            self.stop_button,
            self.seek_slider
        ]:

            widget.configure(
                state=state
            )

    # --------------------------------------
    # LOAD AUDIO FILE
    # --------------------------------------

    def load_audio_file(self, file_path, show_error=True):

        if self.audio_player is None:

            self.player_status_label.configure(
                text="Audio engine is unavailable."
            )

            return False

        try:

            self.audio_player.load_file(file_path)

            self.audio_file_label.configure(
                text=Path(file_path).name
            )

            self.seek_slider.set(0)

            self.set_audio_controls_enabled(True)

            self.player_status_label.configure(
                text="Audio loaded successfully. Ready to play."
            )

            self.time_label.configure(
                text=(
                    "00:00 / "
                    f"{self.format_time(self.audio_player.duration)}"
                )
            )

            return True

        except Exception as error:

            self.player_status_label.configure(
                text="Could not load audio."
            )

            if show_error:

                messagebox.showerror(
                    "Audio Loading Error",
                    str(error),
                    parent=self
                )

            return False

    # --------------------------------------
    # OPEN MP3
    # --------------------------------------

    def open_audio_file(self):

        if self.audio_player is None:
            return

        file_path = filedialog.askopenfilename(
            parent=self,
            title="Open Audio File",
            filetypes=[
                ("MP3 Audio", "*.mp3")
            ]
        )

        if not file_path:
            return

        self.load_audio_file(file_path)

    # --------------------------------------
    # PLAY
    # --------------------------------------

    def play_audio(self):

        if self.audio_player is None:
            return

        try:

            if self.audio_player.file_path is None:

                messagebox.showwarning(
                    "No Audio",
                    "Please open an MP3 file first.",
                    parent=self
                )

                return

            self.audio_player.play()

            self.player_status_label.configure(
                text="Playing audio..."
            )

            self.pause_button.configure(
                text="Ⅱ Pause"
            )

        except Exception as error:

            messagebox.showerror(
                "Playback Error",
                str(error),
                parent=self
            )

    # --------------------------------------
    # PAUSE / RESUME
    # --------------------------------------

    def toggle_pause(self):

        if self.audio_player is None:
            return

        try:

            if self.audio_player.state == "playing":

                self.audio_player.pause()

                self.pause_button.configure(
                    text="▶ Resume"
                )

                self.player_status_label.configure(
                    text="Playback paused."
                )

            elif self.audio_player.state == "paused":

                self.audio_player.resume()

                self.pause_button.configure(
                    text="Ⅱ Pause"
                )

                self.player_status_label.configure(
                    text="Playing audio..."
                )

            else:

                self.play_audio()

        except Exception as error:

            messagebox.showerror(
                "Playback Error",
                str(error),
                parent=self
            )

    # --------------------------------------
    # STOP
    # --------------------------------------

    def stop_audio(self):

        if self.audio_player is None:
            return

        self.audio_player.stop()

        self.seek_slider.set(0)

        self.player_status_label.configure(
            text="Playback stopped."
        )

        self.pause_button.configure(
            text="Ⅱ Pause"
        )

    # --------------------------------------
    # VOLUME
    # --------------------------------------

    def change_playback_volume(self, value):

        if self.audio_player is None:
            return

        self.audio_player.set_volume(
            float(value) / 100
        )

    # --------------------------------------
    # SEEK PREVIEW
    # --------------------------------------

    def preview_seek(self, value):

        if self.audio_player is None:
            return

        duration = self.audio_player.duration

        if duration <= 0:
            return

        target = (
            float(value) / 1000
        ) * duration

        self.time_label.configure(
            text=(
                f"{self.format_time(target)} / "
                f"{self.format_time(duration)}"
            )
        )

    def on_seek_press(self, event=None):

        self._seek_dragging = True

    def on_seek_release(self, event=None):

        self._seek_dragging = False

        self.seek_audio()

    # --------------------------------------
    # SEEK
    # --------------------------------------

    def seek_audio(self):

        if self.audio_player is None:
            return

        if self.audio_player.file_path is None:
            return

        duration = self.audio_player.duration

        if duration <= 0:
            return

        target = (
            float(self.seek_slider.get()) / 1000
        ) * duration

        try:

            self.audio_player.seek(target)

            self.player_status_label.configure(
                text="Playback position updated."
            )

        except Exception as error:

            messagebox.showerror(
                "Seek Error",
                str(error),
                parent=self
            )

    # --------------------------------------
    # UPDATE PLAYER UI
    # --------------------------------------

    def update_audio_ui(self):

        if self.closing:
            return

        if self.audio_player is not None:

            if self.audio_player.file_path is not None:

                try:

                    position = self.audio_player.get_position()

                    duration = self.audio_player.duration

                    # Update timeline
                    if not self._seek_dragging and duration > 0:

                        progress = (
                            position / duration
                        ) * 1000

                        self.seek_slider.set(
                            max(0, min(progress, 1000))
                        )

                    # Update time
                    self.time_label.configure(
                        text=(
                            f"{self.format_time(position)} / "
                            f"{self.format_time(duration)}"
                        )
                    )

                    # Pause button label
                    if self.audio_player.state == "paused":

                        self.pause_button.configure(
                            text="▶ Resume"
                        )

                    else:

                        self.pause_button.configure(
                            text="Ⅱ Pause"
                        )

                    if (
                        self.audio_player.state == "stopped"
                        and position >= duration
                        and duration > 0
                    ):

                        self.player_status_label.configure(
                            text="Playback completed."
                        )

                except Exception as error:

                    self.player_status_label.configure(
                        text=f"Player error: {error}"
                    )

        self.after(
            250,
            self.update_audio_ui
        )

    # ======================================
    # VOICE MANAGER
    # ======================================

    def build_settings(self, parent):

        settings = ctk.CTkScrollableFrame(
            parent,
            corner_radius=16
        )

        settings.grid(
            row=0,
            column=1,
            padx=(10, 0),
            sticky="nsew"
        )

        settings.grid_columnconfigure(
            0,
            weight=1
        )

        # Title
        ctk.CTkLabel(
            settings,
            text="Voice Manager",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        ).grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 15),
            sticky="w"
        )

        # Language
        ctk.CTkLabel(
            settings,
            text="Language"
        ).grid(
            row=1,
            column=0,
            padx=20,
            pady=5,
            sticky="w"
        )

        self.language_menu = ctk.CTkOptionMenu(
            settings,
            values=[
                "فارسی",
                "English",
                "همه زبان‌ها"
            ],
            command=self.refresh_voice_list
        )

        self.language_menu.grid(
            row=2,
            column=0,
            padx=20,
            pady=5,
            sticky="ew"
        )

        self.language_menu.set("فارسی")

        # Gender
        ctk.CTkLabel(
            settings,
            text="Gender"
        ).grid(
            row=3,
            column=0,
            padx=20,
            pady=5,
            sticky="w"
        )

        self.gender_menu = ctk.CTkOptionMenu(
            settings,
            values=[
                "همه",
                "Female",
                "Male"
            ],
            command=self.refresh_voice_list
        )

        self.gender_menu.grid(
            row=4,
            column=0,
            padx=20,
            pady=5,
            sticky="ew"
        )

        self.gender_menu.set("همه")

        # Search
        ctk.CTkLabel(
            settings,
            text="Search Voice"
        ).grid(
            row=5,
            column=0,
            padx=20,
            pady=(12, 5),
            sticky="w"
        )

        self.search_entry = ctk.CTkEntry(
            settings,
            placeholder_text="Search by name or language..."
        )

        self.search_entry.grid(
            row=6,
            column=0,
            padx=20,
            pady=5,
            sticky="ew"
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.refresh_voice_list
        )

        # Available voices
        ctk.CTkLabel(
            settings,
            text="Available Voices"
        ).grid(
            row=7,
            column=0,
            padx=20,
            pady=(12, 5),
            sticky="w"
        )

        self.voice_menu = ctk.CTkOptionMenu(
            settings,
            values=["Loading..."]
        )

        self.voice_menu.grid(
            row=8,
            column=0,
            padx=20,
            pady=5,
            sticky="ew"
        )

        self.voice_menu.configure(
            state="disabled"
        )

        # Refresh
        self.refresh_button = ctk.CTkButton(
            settings,
            text="Refresh Voice List",
            command=self.load_voices,
            fg_color="gray"
        )

        self.refresh_button.grid(
            row=9,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        # Speech speed
        self.rate_slider = self.add_slider(
            settings,
            row=10,
            title="Speech Speed",
            suffix="%"
        )

        # Pitch
        self.pitch_slider = self.add_slider(
            settings,
            row=11,
            title="Pitch",
            suffix="Hz"
        )

        # Speech volume
        self.volume_slider = self.add_slider(
            settings,
            row=12,
            title="Speech Volume",
            suffix="%"
        )

        # Convert
        self.convert_button = ctk.CTkButton(
            settings,
            text="Convert to MP3",
            height=45,
            font=ctk.CTkFont(
                size=16,
                weight="bold"
            ),
            command=self.start_conversion
        )

        self.convert_button.grid(
            row=13,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="ew"
        )

        # Progress
        self.progress = ctk.CTkProgressBar(
            settings,
            mode="indeterminate"
        )

        self.progress.grid(
            row=14,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )

        self.progress.stop()

        # Status
        self.status_label = ctk.CTkLabel(
            settings,
            text="Initializing...",
            text_color="gray",
            wraplength=280
        )

        self.status_label.grid(
            row=15,
            column=0,
            padx=20,
            pady=(5, 15)
        )

    # ======================================
    # SLIDER HELPER
    # ======================================

    def add_slider(
        self,
        parent,
        row,
        title,
        suffix
    ):

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        frame.grid(
            row=row,
            column=0,
            padx=20,
            pady=8,
            sticky="ew"
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            frame,
            text=title
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        value_label = ctk.CTkLabel(
            frame,
            text=f"+0{suffix}",
            text_color="gray"
        )

        value_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        def update_value(value):

            value_label.configure(
                text=f"{int(value):+d}{suffix}"
            )

        slider = ctk.CTkSlider(
            frame,
            from_=-50,
            to=50,
            command=update_value
        )

        slider.set(0)

        slider.grid(
            row=1,
            column=0,
            columnspan=2,
            pady=8,
            sticky="ew"
        )

        return slider

    # ======================================
    # LOAD VOICES
    # ======================================

    def load_voices(self):

        if self.voice_loading:
            return

        self.voice_loading = True

        self.refresh_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Downloading available voices..."
        )

        self.voice_menu.configure(
            values=["Loading..."],
            state="disabled"
        )

        worker = threading.Thread(
            target=self.voice_loading_worker,
            daemon=True
        )

        worker.start()

    def voice_loading_worker(self):

        try:

            voices = fetch_available_voices()

            self.worker_queue.put(
                ("voices_loaded", voices)
            )

        except Exception as error:

            self.worker_queue.put(
                ("voices_error", str(error))
            )

    # ======================================
    # FILTER VOICES
    # ======================================

    def refresh_voice_list(self, value=None):

        if not self.all_voices:
            return

        language = self.language_menu.get()

        gender = self.gender_menu.get()

        search = self.search_entry.get()

        filtered = filter_voices(
            self.all_voices,
            language=language,
            gender=gender,
            search=search
        )

        previous_selection = self.voice_map.get(
            self.voice_menu.get()
        )

        self.voice_map = {}

        display_values = []

        for voice in filtered:

            name = voice.get("ShortName", "")
            locale = voice.get("Locale", "")
            gender_name = voice.get("Gender", "")

            if not name:
                continue

            display = (
                f"{name} | {locale} | {gender_name}"
            )

            self.voice_map[display] = name

            display_values.append(display)

        if not display_values:

            self.voice_menu.configure(
                values=["No matching voices"],
                state="disabled"
            )

            self.voice_menu.set(
                "No matching voices"
            )

            self.status_label.configure(
                text="No voices found."
            )

            return

        self.voice_menu.configure(
            values=display_values,
            state="normal"
        )

        # Preserve selected voice after filtering
        selected = next(
            (
                item for item in display_values
                if self.voice_map[item] == previous_selection
            ),
            None
        )

        # Default voices
        if selected is None:

            preferred_voices = {
                "فارسی": "fa-IR-DilaraNeural",
                "English": "en-US-AriaNeural"
            }

            preferred = preferred_voices.get(
                language
            )

            selected = next(
                (
                    item for item in display_values
                    if self.voice_map[item] == preferred
                ),
                display_values[0]
            )

        self.voice_menu.set(selected)

        self.status_label.configure(
            text=f"{len(display_values)} voices available."
        )

    # ======================================
    # TEXT EDITOR
    # ======================================

    def update_counter(self, event=None):

        text = self.text_box.get(
            "1.0",
            "end-1c"
        )

        self.counter_label.configure(
            text=f"{len(text):,} characters"
        )

    def clear_text(self):

        self.text_box.delete(
            "1.0",
            "end"
        )

        self.update_counter()

    # ======================================
    # START CONVERSION
    # ======================================

    def start_conversion(self):

        if self.is_busy:
            return

        text = self.text_box.get(
            "1.0",
            "end-1c"
        ).strip()

        if not text:

            messagebox.showwarning(
                "Empty Text",
                "Please enter some text first.",
                parent=self
            )

            return

        voice_display = self.voice_menu.get()

        voice = self.voice_map.get(
            voice_display
        )

        if not voice:

            messagebox.showwarning(
                "Voice Selection",
                "Please select a valid voice.",
                parent=self
            )

            return

        output_dir = Path("output")

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = filedialog.asksaveasfilename(
            parent=self,
            title="Save Audio",
            initialdir=str(output_dir.resolve()),
            defaultextension=".mp3",
            initialfile="nova_speech.mp3",
            filetypes=[
                ("MP3 Audio", "*.mp3")
            ]
        )

        if not output_file:
            return

        if Path(output_file).exists():

            overwrite = messagebox.askyesno(
                "Overwrite File",
                "This file already exists. Replace it?",
                parent=self
            )

            if not overwrite:
                return

        rate = (
            f"{int(self.rate_slider.get()):+d}%"
        )

        volume = (
            f"{int(self.volume_slider.get()):+d}%"
        )

        pitch = (
            f"{int(self.pitch_slider.get()):+d}Hz"
        )

        self.is_busy = True

        self.convert_button.configure(
            state="disabled",
            text="Converting..."
        )

        self.status_label.configure(
            text="Generating audio..."
        )

        self.progress.start()

        worker = threading.Thread(
            target=self.conversion_worker,
            args=(
                text,
                voice,
                output_file,
                rate,
                volume,
                pitch
            ),
            daemon=True
        )

        worker.start()

    # ======================================
    # CONVERSION WORKER
    # ======================================

    def conversion_worker(
        self,
        text,
        voice,
        output_file,
        rate,
        volume,
        pitch
    ):

        try:

            asyncio.run(
                synthesize_text(
                    text=text,
                    voice=voice,
                    output_file=output_file,
                    rate=rate,
                    volume=volume,
                    pitch=pitch
                )
            )

            self.worker_queue.put(
                ("success", output_file)
            )

        except Exception as error:

            self.worker_queue.put(
                ("error", str(error))
            )

    # ======================================
    # MESSAGE QUEUE
    # ======================================

    def process_worker_messages(self):

        if self.closing:
            return

        while True:

            try:

                result_type, data = (
                    self.worker_queue.get_nowait()
                )

            except queue.Empty:

                break

            # Voices loaded
            if result_type == "voices_loaded":

                self.all_voices = data

                self.voice_loading = False

                self.refresh_button.configure(
                    state="normal"
                )

                self.refresh_voice_list()

            # Voices error
            elif result_type == "voices_error":

                self.voice_loading = False

                self.refresh_button.configure(
                    state="normal"
                )

                self.status_label.configure(
                    text="Could not load voices."
                )

                messagebox.showerror(
                    "Voice Manager Error",
                    data,
                    parent=self
                )

            # Conversion success
            elif result_type == "success":

                self.finish_success(data)

            # Conversion error
            elif result_type == "error":

                self.finish_error(data)

        self.after(
            100,
            self.process_worker_messages
        )

    # ======================================
    # CONVERSION SUCCESS
    # ======================================

    def finish_success(self, output_file):

        self.is_busy = False

        self.progress.stop()

        self.convert_button.configure(
            state="normal",
            text="Convert to MP3"
        )

        # Automatically load generated audio
        loaded = self.load_audio_file(
            output_file,
            show_error=False
        )

        if loaded:

            self.status_label.configure(
                text=f"Saved: {Path(output_file).name}"
            )

            self.player_status_label.configure(
                text="New audio loaded. Press Play to listen."
            )

        else:

            self.status_label.configure(
                text=f"Saved: {Path(output_file).name}"
            )

        messagebox.showinfo(
            "Success",
            (
                "Audio created successfully!\n\n"
                f"{output_file}\n\n"
                "The file is ready in the Audio Player."
                if loaded
                else
                "Audio saved successfully.\n\n"
                f"{output_file}"
            ),
            parent=self
        )

    # ======================================
    # CONVERSION ERROR
    # ======================================

    def finish_error(self, error):

        self.is_busy = False

        self.progress.stop()

        self.convert_button.configure(
            state="normal",
            text="Convert to MP3"
        )

        self.status_label.configure(
            text="Conversion failed."
        )

        messagebox.showerror(
            "Conversion Error",
            error,
            parent=self
        )

    # ======================================
    # THEME
    # ======================================

    def toggle_theme(self):

        if self.current_appearance == "Dark":

            self.current_appearance = "Light"

        else:

            self.current_appearance = "Dark"

        ctk.set_appearance_mode(
            self.current_appearance
        )

    # ======================================
    # CLOSE APPLICATION
    # ======================================

    def on_close(self):

        if self.is_busy or self.voice_loading:

            answer = messagebox.askyesno(
                "Exit",
                "A background task is still running. Exit anyway?",
                parent=self
            )

            if not answer:
                return

        self.closing = True

        if self.audio_player is not None:

            try:
                self.audio_player.close()

            except Exception:
                pass

        self.destroy()


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    ctk.set_appearance_mode("Dark")

    ctk.set_default_color_theme("blue")

    app = NovaTTSApp()

    app.mainloop()
