# TTS Tools

A collection of tools for text-to-speech processing using ChatterboxTTS, a state-of-the-art open-source multilingual TTS model.

## Overview

This project provides an easy-to-use implementation of ChatterboxTTS for generating high-quality speech from text with voice cloning capabilities. ChatterboxTTS supports 23 languages and offers emotion exaggeration control with robust multilingual zero-shot voice cloning.

## Features

- High-quality text-to-speech synthesis
- Voice cloning from audio samples
- Support for 23 languages
- Emotion exaggeration control
- Optimized for Apple Silicon (MPS) and CPU

## Requirements

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- macOS (Apple Silicon optimized) or Linux

## Installation

### Using uv (Recommended)

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone https://github.com/andrewjamesford/tts-tools.git
cd tts-tools
```

3. Install dependencies:
```bash
uv sync
```

### Using pip

```bash
pip install -r pyproject.toml
```

## Usage

### Basic Text-to-Speech

Run the included example script:

```bash
uv run tts.py
```

This will generate speech from the sample text and save it to `test-2.wav`.

### Voice Cloning

To clone a voice, provide an audio sample:

1. Place your audio sample (WAV format) in the project directory
2. Update the `AUDIO_PROMPT_PATH` in `tts.py`:

```python
AUDIO_PROMPT_PATH = "your_audio_sample.wav"
```

3. Run the script:

```bash
uv run tts.py
```

### Customizing Generation

You can adjust various parameters in `tts.py`:

```python
wav = model.generate(
    text,
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.5,  # Emotion exaggeration (0.0 to 1.0)
    cfg_weight=0.5     # Classifier-free guidance weight
)
```

## Project Structure

```
tts-tools/
├── tts.py              # Main TTS generation script
├── main.py             # Entry point
├── pyproject.toml      # Project dependencies
├── README.md           # This file
└── .gitignore          # Git ignore patterns
```

## Dependencies

Key dependencies include:

- `chatterbox-tts` - Core TTS model
- `torch` - Deep learning framework
- `torchaudio` - Audio processing
- `transformers` - Transformer models
- `diffusers` - Diffusion models
- `librosa` - Audio analysis
- `numpy` - Numerical computing

See `pyproject.toml` for the complete list.

## Known Issues and Workarounds

### PerthImplicitWatermarker Bug

The current version includes a workaround for a bug in `resemble-perth==1.0.1` where `PerthImplicitWatermarker` returns `None`. The script automatically falls back to `DummyWatermarker`:

```python
if perth.PerthImplicitWatermarker is None:
    perth.PerthImplicitWatermarker = perth.DummyWatermarker
```

### First Run

On the first run, the script will download the ChatterboxTTS model files (approximately 2.1 GB). This is a one-time download and will be cached for future use.

## Performance

Generation time depends on:
- Text length
- Hardware capabilities
- Selected parameters

On Apple Silicon (M1/M2/M3/M4), expect approximately 7-8 iterations per second during sampling.

## Supported Languages

ChatterboxTTS supports 23 languages including:
- English
- French
- Spanish
- Japanese
- Chinese
- German
- Italian
- Portuguese
- Russian
- And more...

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project uses ChatterboxTTS, which is licensed under the MIT License by Resemble AI.

## Acknowledgments

- [ChatterboxTTS](https://github.com/resemble-ai/chatterbox) by Resemble AI
- [Perth Audio Watermarker](https://github.com/resemble-ai/Perth) by Resemble AI

## References

- [ChatterboxTTS Documentation](https://github.com/resemble-ai/chatterbox)
- [Resemble AI Blog](https://www.resemble.ai/introducing-chatterbox-multilingual-open-source-tts-for-23-languages/)

## Support

For issues related to:
- This project: Open an issue on this repository
- ChatterboxTTS: See the [official repository](https://github.com/resemble-ai/chatterbox/issues)

## Changelog

### v0.1.0 (Initial Release)
- Basic ChatterboxTTS integration
- Voice cloning support
- Apple Silicon optimization
- Dependency fixes for uv compatibility
