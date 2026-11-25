# 🎙️ Nova TTS – Text to Audio Studio

**Nova TTS** is a desktop-based Text-to-Speech application developed with Python. It allows users to convert written text into natural-sounding speech and save the generated audio as MP3 files.

The application provides a modern graphical interface, voice management, speech customization, and a built-in audio player for listening to generated audio files.

## ✨ Features

- **Text-to-Speech Conversion:** Convert written text into speech using Microsoft Edge TTS.
- **Multiple Voices:** Access a wide range of available voices.
- **Language Filtering:** Filter voices by Persian, English, or all available languages.
- **Gender Filtering:** Select male or female voices.
- **Voice Search:** Search for voices by name, language, or other available information.
- **Speech Customization:**
  - Adjust speech speed.
  - Change voice pitch.
  - Control speech volume.
- **MP3 Export:** Save generated audio files in MP3 format.
- **Built-in Audio Player:**
  - Play audio.
  - Pause and resume playback.
  - Stop playback.
  - Seek through the audio timeline.
  - Adjust playback volume.
  - Open and play existing MP3 files.
- **Modern GUI:** A user-friendly interface built with CustomTkinter.
- **Dark Mode:** Toggle the application's appearance.
- **Background Processing:** Perform voice loading and audio generation in background threads to keep the interface responsive.

## 🛠️ Technologies Used

The project is developed using the following technologies and libraries:

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| CustomTkinter | Modern graphical user interface |
| Edge TTS | Text-to-Speech engine |
| Pygame CE | Audio playback |
| Mutagen | MP3 metadata and duration detection |
| Asyncio | Asynchronous audio generation |
| Threading | Background task execution |

## 📁 Project Structure

```text
Text-to-Audio/
│
├── main.py
│   └── Main application and graphical interface
│
├── tts_engine.py
│   └── Text-to-Speech conversion engine
│
├── voice_manager.py
│   └── Voice retrieval, filtering, and management
│
├── audio_player.py
│   └── Audio playback and control system
│
├── requirements.txt
│   └── Project dependencies
│
├── README.md
│   └── Project documentation
│
└── .gitignore
    └── Git ignored files
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone "https://github.com/amirmahdialmasi/text-to-speak"
```

### 2. Navigate to the Project Directory

```bash
cd Text-to-Audio
```

### 3. Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate the environment:

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Usage

Run the application using:

```bash
python main.py
```

### How to Use

1. Launch the Nova TTS application.
2. Enter your desired text in the Text Editor.
3. Choose a language and filter the available voices.
4. Select your preferred voice.
5. Adjust speech speed, pitch, and volume.
6. Click **Convert to MP3**.
7. Choose the destination for the generated audio file.
8. Once conversion is complete, the audio is automatically loaded into the built-in audio player.
9. Play, pause, seek, or adjust the playback volume as needed.

## 📦 Dependencies

The project uses the following Python packages:

```text
customtkinter
edge-tts
pygame-ce
mutagen
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## 🌐 Internet Connection

An active internet connection is required for retrieving available voices and generating speech through the Edge TTS service.

## 🎯 Project Goals

The main goal of Nova TTS is to provide a simple and efficient desktop solution for converting text into speech.

The project combines voice management, speech customization, MP3 generation, and audio playback in one application with a modern graphical interface.

## 👨‍💻 Developer

**Project Name:** Nova TTS  
**Project Type:** Desktop Text-to-Speech Application  
**Programming Language:** Python  
**Version:** 3.0

---

*Nova TTS – Turning Text into Voice.*