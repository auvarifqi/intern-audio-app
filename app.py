import streamlit as st
import pandas as pd
import os
from pathlib import Path
import re
import streamlit.components.v1 as components
from audiorecorder import audiorecorder
from device_selector import device_selector

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
    audio_folder = Path("audio_recordings") / f"{date}_transcriptions"
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

def save_csv_changes(csv_path, transcriptions, transcription_col):
    """
    Save modified transcriptions back to CSV file
    """
    try:
        # Read original CSV to preserve other columns
        df = pd.read_csv(csv_path)
        # Update the transcription column
        df[transcription_col] = transcriptions + [None] * (len(df) - len(transcriptions))
        # Save back to CSV
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"❌ Error saving CSV: {str(e)}")
        return False
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
    if 'transcription_col' not in st.session_state:
        st.session_state.transcription_col = None
    if 'audio_saved' not in st.session_state:
        st.session_state.audio_saved = False

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
            st.session_state.transcription_col = transcription_col
            st.session_state.date_folder = create_audio_folder(date)
            st.session_state.csv_loaded = True
            st.session_state.audio_saved = False  # Reset audio state for new CSV
            
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

        # ADD THIS: Device selector
        st.subheader("🎧 Select Microphone (Optional)")
        device_selector()
    
         # Add JavaScript to get selected device info
        get_device_info = """
        <script>
        const selectedId = sessionStorage.getItem('selectedMicrophoneId');
        const selectedLabel = sessionStorage.getItem('selectedMicrophoneLabel');
        
        if (selectedId && selectedLabel) {
            // Send info back to Streamlit (optional)
            console.log('Selected microphone:', selectedLabel);
        }
        </script>
        """
        components.html(get_device_info, height=0)
        
        total = len(st.session_state.transcriptions)
        current = st.session_state.current_index + 1
        
        # Progress bar
        progress = (st.session_state.current_index) / total
        st.progress(progress)
        st.write(f"**Progress: {len([f for f in os.listdir(st.session_state.date_folder) if f.endswith('.wav')])}/{total} completed**")
        
        # Check if all recordings are done
        if st.session_state.current_index >= total:
            st.success("🎉 All recordings completed!")
            st.balloons()
            if st.button("🔄 Reset to start over"):
                for key in ['transcriptions', 'current_index', 'date_folder', 'csv_loaded', 'selected_csv', 'transcription_col', 'audio_saved']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            return
        
        # Show current transcription
        current_text = st.session_state.transcriptions[st.session_state.current_index]
        st.subheader(f"Recording #{current}")
        
        # Editable transcription text
        st.write("📝 **Edit transcription if needed:**")
        edited_text = st.text_area(
            "Transcription text:",
            value=current_text,
            height=100,
            help="You can modify this text before recording. Changes will be saved to CSV."
        )
        
        # Save text changes to CSV
        if edited_text != current_text:
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("💾 Save Text"):
                    # Update transcriptions in session state
                    st.session_state.transcriptions[st.session_state.current_index] = edited_text
                    
                    # Save to CSV file
                    csv_path = Path("csvs") / st.session_state.selected_csv
                    if save_csv_changes(csv_path, st.session_state.transcriptions, st.session_state.transcription_col):
                        st.success("✅ Text saved to CSV!")
                        st.rerun()
        
        # Display transcription in a nice box
        st.info(f"📝 **Read this text:**\n\n{edited_text}")
        
        # Audio recording widget
        st.write("🎙️ **Click to start/stop recording:**")
        audio = audiorecorder("Start recording", "Stop recording", show_visualizer=True,
            custom_style={'color': '#34495e'},
            start_style={'backgroundColor': '#34495e', 'color': 'white'},
            stop_style={'backgroundColor': '#e74c3c', 'color': 'white'})
        
        # Show audio when it's recorded
        if len(audio) > 0:
            # Display the recorded audio
            st.audio(audio.export().read(), format="audio/wav")
            
            # Save button
            if st.button("💾 Save Recording & Continue", type="primary"):
                try:
                    # Save audio file
                    audio_filename = f"{current}.wav"
                    audio_path = os.path.join(st.session_state.date_folder, audio_filename)
                    
                    # Export and save audio
                    audio.export(audio_path, format="wav")
                    
                    st.success(f"✅ Saved: {audio_filename}")
                    
                    # Move to next transcription
                    st.session_state.current_index += 1
                    
                    # Small delay and rerun
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error saving audio: {str(e)}")
        else:
            st.info("🎤 Click the microphone to start recording.")
        
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
                for key in ['transcriptions', 'current_index', 'date_folder', 'csv_loaded', 'selected_csv', 'transcription_col']:
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
            st.write(f"**Completed:** {len([f for f in os.listdir(st.session_state.date_folder) if f.endswith('.wav')])}")
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