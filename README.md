# 🎵 Curvora

**HiFi Audio Waveform Analyzer & Manipulator**

Curvora 是一款基于 Web 的高保真音频分析与处理工具，支持交互式波形/频谱可视化、采样率倍增（最高 192kHz）以及多种专业级重采样算法。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54+-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🔍 Interactive Visualization
- **Waveform** — 时间轴 vs 振幅，支持鼠标拖拽缩放、平移浏览
- **Spectrogram** — 对数频率热力图，自适应 FFT 窗口（高采样率自动使用 n_fft=4096）
- **Sample Points** — 可选叠加显示采样点（红色圆点），适合放大后观察细节
- 基于 **Plotly** 构建，所有图表均支持缩放、平移、悬停查看数值

### 🎵 HiFi Resampling (采样率倍增)
支持将音频重采样至以下采样率：

| 采样率 | 用途 |
|--------|------|
| 8 kHz | 电话语音 |
| 16 kHz | 语音识别 |
| 22.05 kHz | AM 广播 |
| 44.1 kHz | CD 标准 |
| 48 kHz | 专业音频/视频 |
| 88.2 kHz | HiFi 2x |
| 96 kHz | HiFi / Studio |
| 176.4 kHz | HiFi 4x |
| 192 kHz | Ultra HiFi / Mastering |

### 🧮 Resampling Algorithms (重采样算法)

| 算法 | 质量 | 速度 | 说明 |
|------|------|------|------|
| `soxr_vhq` | ⭐⭐⭐⭐⭐ | 较慢 | SoX Very High Quality — HiFi 首选，最佳频谱保真度 |
| `soxr_hq` | ⭐⭐⭐⭐ | 快 | SoX High Quality — 日常使用推荐 |
| `scipy_polyphase` | ⭐⭐⭐⭐ | 中等 | 多相 FIR 滤波器，优秀的抗混叠性能 |
| `linear` | ⭐⭐ | 极快 | 线性插值，适合快速预览 |

### 🔊 Audio Processing (音频处理)
- **Gain (增益)** — 0.0x ~ 3.0x 音量调节
- **Clipping (硬裁剪)** — 限制最大振幅，防止削波失真
- **Export (导出)** — 处理后音频一键下载为 WAV 文件

### 📊 Info Panel (信息面板)
- 文件名、时长、原始采样率
- 通道数（单声道/立体声）
- 原始/处理后采样数对比
- 输出采样率与倍率显示

---

## 🚀 Quick Start

### 环境要求
- Python 3.10+
- pip

### 安装 & 运行

```bash
# 克隆项目
git clone git@github.com:Eronwu/curvora_web.git
cd curvora_web

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`，上传音频文件即可开始分析。

### 支持的音频格式
- WAV
- MP3
- OGG
- FLAC

---

## 🛠️ Tech Stack

| 组件 | 用途 |
|------|------|
| [Streamlit](https://streamlit.io/) | Web UI 框架 |
| [Librosa](https://librosa.org/) | 音频分析（加载、STFT、重采样） |
| [Plotly](https://plotly.com/python/) | 交互式图表（缩放/平移/悬停） |
| [SoXR](https://github.com/dofuuz/python-soxr) | 高质量重采样引擎 |
| [SciPy](https://scipy.org/) | 多相滤波器重采样 |
| [SoundFile](https://pysoundfile.readthedocs.io/) | 音频文件读写 |
| [NumPy](https://numpy.org/) | 数值计算 |

---

## 📁 Project Structure

```
curvora_web/
├── app.py              # 主应用程序
├── requirements.txt    # Python 依赖
├── README.md           # 项目说明
└── venv/               # 虚拟环境（不提交）
```

---

## 🗺️ Roadmap

- [ ] 多通道（立体声）独立波形显示
- [ ] 频率滤波器（高通/低通/带通）
- [ ] A/B 对比模式（处理前 vs 处理后）
- [ ] 批量文件处理
- [ ] Flutter 跨平台版本
- [ ] 音频格式转换（FLAC/AAC/OGG）

---

## 📄 License

MIT License — 自由使用、修改和分发。

---

## 🙏 Acknowledgments

Built with ❤️ by [Eron Wu](https://github.com/Eronwu)

Powered by the amazing open-source audio ecosystem: Librosa, SoXR, Plotly, and Streamlit.
