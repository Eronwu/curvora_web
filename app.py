import streamlit as st
import librosa
import librosa.display
import numpy as np
import soundfile as sf
import plotly.graph_objects as go
from scipy import signal as scipy_signal
import io

st.set_page_config(page_title="Audio Waveform Analyzer", layout="wide")

st.title("Audio Waveform Analyzer & Manipulator")

uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg", "flac"])

if uploaded_file is not None:
    try:
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
        st.write(f"**Samples:** {len(y):,}")
        st.write(f"**Channels:** {'Mono' if len(y.shape) == 1 else 'Stereo'}")

        st.markdown("---")

        # === Gain ===
        st.subheader("🔊 Gain")
        gain = st.slider("Volume Gain", 0.0, 3.0, 1.0, 0.05)
        clip_threshold = st.slider("Clipping Threshold", 0.05, 1.0, 1.0, 0.05)

        st.markdown("---")

        # === HiFi Resampling ===
        st.subheader("🎵 HiFi Resampling")

        # Build SR options: original + standard rates
        sr_options = sorted(set([8000, 16000, 22050, 44100, 48000, 88200, 96000, 176400, 192000, sr]))
        sr_labels = {s: f"{s/1000:.1f} kHz" + (" (original)" if s == sr else "") for s in sr_options}
        default_idx = sr_options.index(sr)

        target_sr = st.selectbox(
            "Target Sample Rate",
            sr_options,
            index=default_idx,
            format_func=lambda x: sr_labels[x]
        )

        # Upsampling algorithm selection
        resample_algo = st.selectbox(
            "Resampling Algorithm",
            ["soxr_hq", "soxr_vhq", "scipy_polyphase", "linear"],
            index=1,
            help=(
                "**soxr_hq**: High quality SoX resampler (fast, great quality)\n\n"
                "**soxr_vhq**: Very high quality SoX (best for HiFi, slower)\n\n"
                "**scipy_polyphase**: Polyphase FIR filter (good anti-aliasing)\n\n"
                "**linear**: Simple linear interpolation (fast, lower quality)"
            )
        )

        if target_sr != sr:
            ratio = target_sr / sr
            st.write(f"**Multiplier:** {ratio:.2f}x {'(upsampling)' if ratio > 1 else '(downsampling)'}")

        st.markdown("---")

        # === Waveform Display Options ===
        st.subheader("📊 Waveform Display")
        show_sample_points = st.checkbox("Show Sample Points", value=False,
            help="Display individual sample points as dots on the waveform. Best used when zoomed in.")
        display_points = st.slider("Display Points (max)", 2000, 50000, 10000, 1000,
            help="More points = more detail but slower rendering")

        st.markdown("---")

        # === Processing ===
        # 1. Apply gain
        y_processed = y * gain

        # 2. Apply clipping
        y_processed = np.clip(y_processed, -clip_threshold, clip_threshold)

        # 3. Resampling with selected algorithm
        if target_sr != sr:
            if resample_algo == "soxr_hq":
                y_processed = librosa.resample(y_processed, orig_sr=sr, target_sr=target_sr, res_type='soxr_hq')
            elif resample_algo == "soxr_vhq":
                y_processed = librosa.resample(y_processed, orig_sr=sr, target_sr=target_sr, res_type='soxr_vhq')
            elif resample_algo == "scipy_polyphase":
                # Use scipy's polyphase resampling for high-quality FIR filtering
                from fractions import Fraction
                frac = Fraction(target_sr, sr).limit_denominator(1000)
                y_processed = scipy_signal.resample_poly(y_processed, frac.numerator, frac.denominator)
            elif resample_algo == "linear":
                # Simple linear interpolation
                num_samples = int(len(y_processed) * target_sr / sr)
                x_old = np.linspace(0, 1, len(y_processed))
                x_new = np.linspace(0, 1, num_samples)
                y_processed = np.interp(x_new, x_old, y_processed)
            current_sr = target_sr
        else:
            current_sr = sr

        # Show post-processing info
        st.write(f"**Output SR:** {current_sr/1000:.1f} kHz")
        st.write(f"**Output Samples:** {len(y_processed):,}")

        st.markdown("---")

        # Export
        buffer = io.BytesIO()
        sf.write(buffer, y_processed.T if len(y_processed.shape) > 1 else y_processed, current_sr, format='WAV')
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Processed Audio (WAV)",
            data=buffer,
            file_name=f"processed_{uploaded_file.name.rsplit('.', 1)[0]}_{current_sr}Hz.wav",
            mime="audio/wav"
        )

    with col1:
        st.header("Visual Analysis")

        # === Waveform (Interactive Plotly) ===
        st.subheader("Waveform")

        # Decimate for display performance
        step = max(1, len(y_processed) // display_points)
        x_plot = np.linspace(0, len(y_processed) / current_sr, num=len(y_processed))[::step]
        y_plot = y_processed[::step]

        # Line trace
        traces = [go.Scatter(
            x=x_plot, y=y_plot,
            mode='lines',
            line=dict(color='steelblue', width=1),
            name='Waveform'
        )]

        # Sample points overlay
        if show_sample_points:
            # Show more points when sample points enabled, but cap at display_points
            sp_step = max(1, len(y_processed) // display_points)
            x_sp = np.linspace(0, len(y_processed) / current_sr, num=len(y_processed))[::sp_step]
            y_sp = y_processed[::sp_step]
            traces.append(go.Scatter(
                x=x_sp, y=y_sp,
                mode='markers',
                marker=dict(color='orangered', size=3),
                name='Sample Points'
            ))

        fig_wave = go.Figure(data=traces)
        fig_wave.update_layout(
            title=f'Waveform — {len(y_processed):,} samples @ {current_sr/1000:.1f} kHz',
            xaxis_title='Time (s)',
            yaxis_title='Amplitude',
            margin=dict(l=0, r=0, t=40, b=0),
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig_wave, use_container_width=True)

        # === Spectrogram (Interactive Plotly) ===
        st.subheader("Spectrogram")

        # Use adaptive n_fft based on sample rate for better resolution
        n_fft = 4096 if current_sr >= 96000 else 2048
        hop_length = n_fft // 4

        D = np.abs(librosa.stft(y_processed, n_fft=n_fft, hop_length=hop_length))
        D_db = librosa.amplitude_to_db(D, ref=np.max)

        # Downsample the spectrogram matrix if too large for Plotly
        max_time_bins = 2000
        max_freq_bins = 1024
        if D_db.shape[1] > max_time_bins:
            t_step = D_db.shape[1] // max_time_bins
            D_db = D_db[:, ::t_step]
        if D_db.shape[0] > max_freq_bins:
            f_step = D_db.shape[0] // max_freq_bins
            D_db = D_db[::f_step, :]

        times = np.linspace(0, len(y_processed) / current_sr, D_db.shape[1])
        freqs_full = librosa.fft_frequencies(sr=current_sr, n_fft=n_fft)
        if len(freqs_full) > D_db.shape[0]:
            f_step2 = len(freqs_full) // D_db.shape[0]
            freqs_display = freqs_full[::f_step2][:D_db.shape[0]]
        else:
            freqs_display = freqs_full[:D_db.shape[0]]

        fig_spec = go.Figure(data=go.Heatmap(
            z=D_db,
            x=times,
            y=freqs_display,
            colorscale='Viridis',
            zmin=-80, zmax=0,
            colorbar=dict(title='dB')
        ))
        fig_spec.update_layout(
            title=f'Spectrogram (dB) — n_fft={n_fft}, max freq={current_sr//2:,} Hz',
            xaxis_title='Time (s)',
            yaxis_title='Frequency (Hz)',
            yaxis_type='log',
            margin=dict(l=0, r=0, t=40, b=0),
            height=500
        )
        st.plotly_chart(fig_spec, use_container_width=True)

        # === Audio Preview ===
        st.subheader("Preview")
        st.audio(buffer, format='audio/wav')

else:
    st.info("👆 Please upload an audio file (WAV, MP3, OGG, FLAC) to begin.")
