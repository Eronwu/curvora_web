import streamlit as st
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import plotly.graph_objects as go
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

        # Plot Waveform (Interactive via Plotly)
        st.subheader("Waveform")
        # Downsample for performance if needed, but here we plot full or strided
        # Plotly can handle ~100k points, but audio has millions. Let's decimate for display.
        step = max(1, len(y_processed) // 5000)
        x_plot = np.linspace(0, len(y_processed)/current_sr, num=len(y_processed))[::step]
        y_plot = y_processed[::step]
        
        fig_wave = go.Figure(data=go.Scatter(x=x_plot, y=y_plot, mode='lines', line=dict(color='steelblue', width=1)))
        fig_wave.update_layout(
            title='Waveform (Amplitude vs Time)',
            xaxis_title='Time (s)',
            yaxis_title='Amplitude',
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig_wave, use_container_width=True)

        # Spectrogram (Interactive via Plotly)
        st.subheader("Spectrogram")
        # Compute STFT
        D = np.abs(librosa.stft(y_processed, n_fft=2048, hop_length=512))
        D_db = librosa.amplitude_to_db(D, ref=np.max)
        
        # Spectrogram can be heavy. Let's plot it as a Heatmap.
        # X axis: Time, Y axis: Frequency
        # We need to construct axis coordinates
        times = librosa.frames_to_time(np.arange(D_db.shape[1]), sr=current_sr, hop_length=512)
        freqs = librosa.fft_frequencies(sr=current_sr, n_fft=2048)
        
        fig_spec = go.Figure(data=go.Heatmap(
            z=D_db, 
            x=times, 
            y=freqs, 
            colorscale='Viridis',
            zmin=-80, zmax=0
        ))
        fig_spec.update_layout(
            title='Spectrogram (dB)',
            xaxis_title='Time (s)',
            yaxis_title='Frequency (Hz)',
            yaxis_type='log',
            margin=dict(l=0, r=0, t=30, b=0),
            height=300
        )
        st.plotly_chart(fig_spec, use_container_width=True)

        # Play Audio
        st.subheader("Preview")
        st.audio(buffer, format='audio/wav')

else:
    st.info("Please upload an audio file to begin.")
