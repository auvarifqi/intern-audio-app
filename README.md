# Audio Recording Application

A Streamlit application for recording audio based on text transcriptions.

## Features
- Load CSV files with transcriptions
- Record audio for each transcription
- Save recordings with automatic numbering
- Track progress and resume recording sessions
- Microphone device selection

## Prerequisites
This application requires FFmpeg to be installed on your system:

- **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg` (requires Homebrew)
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or install via Chocolatey: `choco install ffmpeg`

## Setup
### Clone the Repository
First, clone this repository to your local laptop:

```bash
git clone https://github.com/auvarifqi/intern-audio-app.git
cd intern-audio_app
```

### Automated Setup (Recommended)
Use the provided setup script to create a virtual environment and install dependencies:

```bash
# Make the script executable (Unix/macOS)
chmod +x setup.sh

# Run the setup script
./setup.sh
```

On Windows, you can use Git Bash or WSL to run the script. Example: `bash setup.sh` or `./setup.sh` in Git Bash.

You will be prompted to fill the virtual environment, please follow the prompt.

If the setup script successful, you will see output like this in your terminal:
```bash
🎉 Setup complete! Activate your environment with:
conda activate {your_env}

📝 To run the app after activating the environment:
streamlit run app.py
```

## Run the App
After running the setup script, activate the environment and start the application:
```bash
# Activate the virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
# or if using Conda
conda activate {your_env}  # If you created a conda environment

# Run the application
streamlit run app.py
```


## CSV Format
The CSV file should have a column named 'transcription' or 'transcriptions'.
Filename should follow the format: DD_MM_YYYY_name_transcriptions.csv
