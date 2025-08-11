# Audio Recording Application

A Streamlit application for recording audio based on text transcriptions.

## Features
- Load CSV files with transcriptions
- Record audio for each transcription
- Save recordings with automatic numbering
- Track progress and resume recording sessions

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Place CSV files in the `csvs/` folder
3. Run the app: `streamlit run app.py`

## CSV Format
The CSV file should have a column named 'transcription' or 'transcriptions'.
Filename should follow the format: DD_MM_YYYY_name_transcriptions.csv