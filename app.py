import streamlit as st
import pandas as pd
import os
from pathlib import Path
import re
from audio_recorder_streamlit import audio_recorder

def extract_date_from_filename(filename):
    """
    Extract date from CSV filename
    Example: '11_08_2025_akbar_transcriptions.csv' -> '11_08_2025'
    """
    # Look for pattern: DD_MM_YYYY at the beginning of filename
    match = re.match(r'(\d{2}_\d{2}_\d{4})', filename)
    if match:
        return match.group(1)
    return None

def get_next_audio_number(audio_folder):
    """
    Check existing audio files and return next number to record
    Example: if 1.m4a, 2.m4a exist, return 3
    """
    if not os.path.exists(audio_folder):
        return 1
    
    # Get all .m4a files and extract numbers
    existing_files = []
    for file in os.listdir(audio_folder):
        if file.endswith('.m4a'):
            try:
                # Extract number from filename like "5.m4a" -> 5
                number = int(file.split('.')[0])
                existing_files.append(number)
            except ValueError:
                continue
    
    if not existing_files:
        return 1
    
    # Return the next number after the highest existing
    return max(existing_files) + 1

def create_audio_folder(date):
    """
    Create audio folder structure: audio_recordings/DD_MM_YYYY/
    """
    audio_folder = Path("audio_recordings") / date
    audio_folder.mkdir(parents=True, exist_ok=True)
    return str(audio_folder)

def get_csv_files():
    """
    Get all CSV files from the csvs folder
    """
    csvs_folder = Path("csvs")
    if not csvs_folder.exists():
        csvs_folder.mkdir(exist_ok=True)
        return []
    
    csv_files = list(csvs_folder.glob("*.csv"))
    return [f.name for f in csv_files]

def main():
    st.title("🎙️ Intern Audio Recording App")
    st.markdown("Put your CSV file in the `csvs/` folder and select it below!")
    
    # Initialize session state variables
    if 'transcriptions' not in st.session_state:
        st.session_state.transcriptions = []
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'date_folder' not in st.session_state:
        st.session_state.date_folder = None
    if 'csv_loaded' not in st.session_state:
        st.session_state.csv_loaded = False
    if 'selected_csv' not in st.session_state:
        st.session_state.selected_csv = None

    # Step 1: CSV Selection
    st.header("📁 Step 1: Select CSV File")
    
    # Get available CSV files
    csv_files = get_csv_files()
    
    if not csv_files:
        st.warning("⚠️ No CSV files found in `csvs/` folder!")
        st.info("💡 **Instructions:**\n1. Put your CSV file in the `csvs/` folder\n2. Refresh this page\n3. Select your file below")
        if st.button("🔄 Refresh"):
            st.rerun()
        return
    
    # Select CSV file
    selected_file = st.selectbox(
        "Choose your transcription CSV file:",
        options=[""] + csv_files,
        help="Select file like: 08_08_2025_akbar_transcriptions.csv"
    )
    
    if selected_file and selected_file != st.session_state.selected_csv:
        st.session_state.selected_csv = selected_file
        st.session_state.csv_loaded = False  # Reset loading state
    
    # Load CSV button
    if selected_file and st.button("📖 Load CSV File"):
        # Extract date from filename
        date = extract_date_from_filename(selected_file)
        
        if date is None:
            st.error("❌ Invalid filename format! Please use: DD_MM_YYYY_name_transcriptions.csv")
            return
        
        st.success(f"✅ Date extracted: {date}")
        
        # Read CSV file
        try:
            csv_path = Path("csvs") / selected_file
            df = pd.read_csv(csv_path)
            
            # Check if 'transcriptions' or 'transcription' column exists
            transcription_col = None
            if 'transcriptions' in df.columns:
                transcription_col = 'transcriptions'
            elif 'transcription' in df.columns:
                transcription_col = 'transcription'
            else:
                st.error("❌ CSV must have a 'transcription' or 'transcriptions' column!")
                return
            
            # Store transcriptions in session state
            st.session_state.transcriptions = df[transcription_col].dropna().tolist()
            st.session_state.date_folder = create_audio_folder(date)
            st.session_state.csv_loaded = True
            
            # Check for existing recordings to resume
            next_number = get_next_audio_number(st.session_state.date_folder)
            st.session_state.current_index = next_number - 1
            
            st.success(f"✅ Loaded {len(st.session_state.transcriptions)} transcriptions")
            if next_number > 1:
                st.info(f"📂 Found existing recordings. Resuming from audio #{next_number}")
            
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")
            return

    # Step 2: Recording Interface
    if st.session_state.csv_loaded:
        st.header("🎤 Step 2: Record Audio")
        
        total = len(st.session_state.transcriptions)
        current = st.session_state.current_index + 1
        
        # Progress bar
        progress = (st.session_state.current_index) / total
        st.progress(progress)
        st.write(f"**Progress: {st.session_state.current_index}/{total} completed**")
        
        # Check if all recordings are done
        if st.session_state.current_index >= total:
            st.success("🎉 All recordings completed!")
            st.balloons()
            if st.button("🔄 Reset to start over"):
                for key in ['transcriptions', 'current_index', 'date_folder', 'csv_loaded', 'selected_csv']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            return
        
        # Show current transcription
        current_text = st.session_state.transcriptions[st.session_state.current_index]
        st.subheader(f"Recording #{current}")
        
        # Display transcription in a nice box
        st.info(f"📝 **Read this text:**\n\n{current_text}")
        
        # Audio recording widget
        st.write("🎙️ **Click to start/stop recording:**")
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#e74c3c",
            neutral_color="#34495e",
            icon_name="microphone",
            icon_size="2x",
        )
        
        # When audio is recorded
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            
            # Save button
            if st.button("💾 Save Recording & Continue", type="primary"):
                try:
                    # Save audio file
                    audio_filename = f"{current}.m4a"
                    audio_path = os.path.join(st.session_state.date_folder, audio_filename)
                    
                    # Write audio bytes to file
                    with open(audio_path, "wb") as f:
                        f.write(audio_bytes)
                    
                    st.success(f"✅ Saved: {audio_filename}")
                    
                    # Move to next transcription
                    st.session_state.current_index += 1
                    
                    # Small delay and rerun
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving audio: {str(e)}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Previous") and st.session_state.current_index > 0:
                st.session_state.current_index -= 1
                st.rerun()
        
        with col2:
            if st.button("⏭️ Skip") and st.session_state.current_index < total - 1:
                st.session_state.current_index += 1
                st.rerun()
                
        with col3:
            if st.button("🔄 Reset App"):
                for key in ['transcriptions', 'current_index', 'date_folder', 'csv_loaded', 'selected_csv']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    # Sidebar with information
    with st.sidebar:
        st.header("📊 Information")
        
        if st.session_state.csv_loaded:
            st.write(f"**CSV File:** {st.session_state.selected_csv}")
            st.write(f"**Date:** {os.path.basename(st.session_state.date_folder)}")
            st.write(f"**Audio Folder:** {st.session_state.date_folder}")
            st.write(f"**Total Transcriptions:** {len(st.session_state.transcriptions)}")
            st.write(f"**Completed:** {st.session_state.current_index}")
            st.write(f"**Remaining:** {len(st.session_state.transcriptions) - st.session_state.current_index}")
        else:
            st.write("Put CSV in `csvs/` folder and select it!")
        
        st.markdown("---")
        st.markdown("**Instructions:**")
        st.markdown("1. Put CSV in `csvs/` folder")
        st.markdown("2. Select CSV file")
        st.markdown("3. Read the text aloud")
        st.markdown("4. Record your voice")
        st.markdown("5. Save and continue")

if __name__ == "__main__":
    main()