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

This will generate speech from the sample text and save it to `test.wav`.

### Voice Cloning and Accents

**Important**: The accent (American, British, New Zealand, etc.) comes from your **audio prompt sample**, not the model itself. ChatterboxTTS clones the voice characteristics, including accent, speaking style, and tone from the audio you provide.

#### Changing Accents

To get a specific accent (e.g., New Zealand or English):

1. **Obtain an audio sample** with the desired accent:
   - Record yourself speaking (5-30 seconds)
   - Use royalty-free voice samples
   - Record a friend with the desired accent
   - Find creative commons licensed audio clips

2. **Audio requirements**:
   - Format: WAV (preferred) or MP3
   - Duration: 5-30 seconds (sweet spot: 10-15 seconds)
   - Quality: Clear speech, minimal background noise
   - Content: Natural speaking, single speaker
   - Sample rate: 16kHz or higher recommended

3. **Place your audio file** in the project directory

4. **Update the script**:

```python
# For New Zealand accent
AUDIO_PROMPT_PATH = "nz_accent_sample.wav"

# For British English accent
AUDIO_PROMPT_PATH = "british_accent_sample.wav"
```

5. **Run the script**:

```bash
# Use the New Zealand accent example
uv run tts_nz_accent.py

# Or modify and run the main script
uv run tts.py
```

#### Example Scripts

The project includes example scripts for different use cases:

- `tts.py` - Main script with voice cloning
- `tts_nz_accent.py` - Example configured for New Zealand accent
- `tts_no_voice_clone.py` - Example using default voice (American accent)

### Customizing Generation

You can adjust various parameters to control the output:

```python
wav = model.generate(
    text,
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.5,  # Emotion exaggeration (0.0 to 1.0)
                       # Lower (0.0-0.3): More neutral, natural speech
                       # Higher (0.6-1.0): More expressive, emotional
    cfg_weight=0.5     # Classifier-free guidance weight (0.0 to 1.0)
                       # Lower (0.0-0.4): More creative, varied
                       # Higher (0.6-1.0): More faithful to audio prompt
)
```

**Tips for better accent reproduction:**
- Use `cfg_weight=0.7` or higher to stay closer to your accent sample
- Use `exaggeration=0.3` or lower for more natural, neutral speech
- Ensure your audio sample clearly demonstrates the desired accent

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
