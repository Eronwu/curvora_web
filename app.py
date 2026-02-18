import streamlit as st
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import io

st.set_page_config(page_title="Audio Waveform Analyzer", layout="wide")

st.title("Audio Waveform Analyzer & Manipulator")

# Sidebar for file upload to keep main area clean, or just top of page.
# Requirement says: Left (Visuals), Right (Controls). Let's put upload at the top.

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

if uploaded_file is not None:
    # Load audio
    # librosa.load accepts file path or file-like object.
    # We use the uploaded file directly.
    try:
        # Load with original SR initially to get info
        y, sr = librosa.load(uploaded_file, sr=None)
    except Exception as e:
        st.error(f"Error loading audio: {e}")
        st.stop()

    # Layout: Left (Visuals), Right (Controls)
    col1, col2 = st.columns([3, 1])

    with col2:
        st.header("Controls & Info")
        
        # Info
        duration = librosa.get_duration(y=y, sr=sr)
        st.info(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Duration:** {duration:.2f} s")
        st.write(f"**Original SR:** {sr} Hz")
        st.write(f"**Channels:** {'Mono' if len(y.shape) == 1 else 'Stereo'}")

        st.markdown("---")
        st.subheader("Manipulation")

        # Controls
        gain = st.slider("Gain (Volume)", 0.0, 2.0, 1.0, 0.1)
        clip_threshold = st.slider("Clipping Threshold", 0.1, 1.0, 1.0, 0.05)
        
        target_sr = st.selectbox("Resample (Target SR)", [sr, 44100, 22050, 16000, 8000], index=0)

        # Processing Logic
        y_processed = y * gain
        
        # Clipping (simple hard clipping)
        # Clip values to be within -threshold and +threshold
        y_processed = np.clip(y_processed, -clip_threshold, clip_threshold)

        # Resampling
        if target_sr != sr:
            # librosa.resample works on mono or stereo
            y_processed = librosa.resample(y_processed, orig_sr=sr, target_sr=target_sr)
            current_sr = target_sr
        else:
            current_sr = sr

        st.markdown("---")
        
        # Export
        # Convert to bytes for download
        buffer = io.BytesIO()
        sf.write(buffer, y_processed.T if len(y_processed.shape) > 1 else y_processed, current_sr, format='WAV')
        buffer.seek(0)
        
        st.download_button(
            label="Download Processed Audio (WAV)",
            data=buffer,
            file_name=f"processed_{uploaded_file.name.rsplit('.', 1)[0]}.wav",
            mime="audio/wav"
        )

    with col1:
        st.header("Visual Analysis")

        # Plot Waveform
        st.subheader("Waveform")
        fig_wave, ax_wave = plt.subplots(figsize=(10, 4))
        librosa.display.waveshow(y_processed, sr=current_sr, ax=ax_wave)
        ax_wave.set_title("Amplitude vs Time")
        st.pyplot(fig_wave)

        # Optional: Spectrogram
        st.subheader("Spectrogram")
        fig_spec, ax_spec = plt.subplots(figsize=(10, 4))
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y_processed)), ref=np.max)
        img = librosa.display.specshow(D, sr=current_sr, x_axis='time', y_axis='log', ax=ax_spec)
        fig_spec.colorbar(img, ax=ax_spec, format="%+2.0f dB")
        ax_spec.set_title("Log-Frequency Spectrogram")
        st.pyplot(fig_spec)

        # Play Audio
        st.subheader("Preview")
        st.audio(buffer, format='audio/wav')

else:
    st.info("Please upload an audio file to begin.")
