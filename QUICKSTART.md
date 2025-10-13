# Quick Start Guide - TTS Batch Processor

Get up and running with batch text-to-speech processing in under 5 minutes!

## Prerequisites

- Python 3.10 or higher
- uv package manager installed
- Mac (Apple Silicon) or Linux

## Quick Setup

### 1. Install Dependencies

```bash
uv sync
```

### 2. Test Text Processing (No Audio Generation)

First, verify the text normalization and batching works correctly:

```bash
uv run test_text_processing.py
```

This will show you how your text gets:
- Converted (acronyms and numbers → words)
- Split into chunks
- Prepared for TTS

**Expected output:**
```
================================================================================
TTS BATCH PROCESSOR - TEXT PROCESSING TEST
================================================================================

Original:   The SSD has 512GB storage and 16GB RAM.
Normalized: The S S D has five hundred and twelve gigabyte storage...
```

### 3. Set Up Your Voice Sample

Place your voice sample file in the project directory. Supported formats:
- WAV (recommended)
- MP3
- Any audio format supported by librosa

Recommended: 10-15 seconds of clear speech, single speaker, minimal background noise.

### 4. Configure the Processor

Edit `tts_batch_processor.py` (lines 25-32):

```python
AUDIO_PROMPT_PATH = "your_voice_sample.wav"  # ← Change this
```

Optional adjustments:
```python
BATCH_SIZE_CHARS = 300        # Chunk size (200-500 recommended)
MAX_PARALLEL_CHUNKS = 4       # Parallel workers (2-4 recommended)
EXAGGERATION = 0.3            # Expressiveness (0.2-0.4 for natural)
CFG_WEIGHT = 0.9              # Voice faithfulness (0.8-1.0)
```

### 5. Add Your Text Files

Place `.txt` files in the `input_texts/` folder:

```bash
input_texts/
├── chapter01.txt
├── article.txt
└── notes.txt
```

### 6. Run the Batch Processor

```bash
uv run tts_batch_processor.py
```

**First run:** The model will download (~2.1 GB). This happens once and takes 5-10 minutes depending on your connection.

**Subsequent runs:** Start generating immediately.

### 7. Get Your Audio Files

Check the `output_audio/` folder:

```bash
output_audio/
├── chapter01_00_20251013-1430.wav
├── chapter01_01_20251013-1430.wav
├── chapter01_02_20251013-1430.wav
├── article_00_20251013-1430.wav
└── article_01_20251013-1430.wav
```

## Example Session

```bash
# 1. Add your text file
echo "The new API uses 512GB SSD storage with CPU optimization." > input_texts/test.txt

# 2. Test processing (no audio)
uv run test_text_processing.py

# 3. Generate audio
uv run tts_batch_processor.py
```

## What Gets Converted?

| Input | Output (Spoken) |
|-------|----------------|
| `512GB SSD` | "five hundred twelve gigabyte S S D" |
| `API JSON URL` | "A P I J S O N U R L" |
| `CPU & GPU` | "C P U and G P U" |
| `Price: 1299.99` | "Price: one two nine nine point nine nine" |
| `8.5 seconds` | "eight point five seconds" |
| `NZ and UK` | "N Z and U K" |

## Troubleshooting

### "No .txt files found"
```bash
# Check the folder
ls input_texts/
# Add files
cp your_text.txt input_texts/
```

### "FileNotFoundError: sample03.mp3"
Update `AUDIO_PROMPT_PATH` in `tts_batch_processor.py` to point to your actual voice sample.

### Memory errors
Reduce parallel processing:
```python
MAX_PARALLEL_CHUNKS = 1  # Process one chunk at a time
```

### Slow processing
Increase parallel processing (if you have enough RAM):
```python
MAX_PARALLEL_CHUNKS = 8  # More parallel workers
```

### Model download fails
- Check your internet connection
- Clear the cache: `rm -rf ~/.cache/huggingface/`
- Try again: `uv run tts_batch_processor.py`

## Next Steps

- Read [BATCH_PROCESSOR_README.md](BATCH_PROCESSOR_README.md) for detailed documentation
- Customize acronym conversions for your domain
- Adjust batching parameters for your content type
- Experiment with `EXAGGERATION` and `CFG_WEIGHT` settings

## Quick Reference

### File Structure
```
tts-tools/
├── tts_batch_processor.py      # Main batch processor
├── test_text_processing.py     # Test without audio generation
├── input_texts/                # Put .txt files here
│   ├── example01.txt           # Sample file 1
│   └── TextFile01.txt          # Sample file 2
├── output_audio/               # Generated audio appears here
└── your_voice_sample.wav       # Your voice to clone
```

### Key Configuration Variables

```python
# tts_batch_processor.py (top of file)

ENABLE_BATCHING = True          # Group sentences into chunks
BATCH_SIZE_CHARS = 300          # ~300 chars = 2-3 sentences
MIN_SENTENCE_LENGTH = 30        # Min length before merging
LONG_SENTENCE_THRESHOLD = 500   # Split sentences longer than this

MAX_PARALLEL_CHUNKS = 4         # Parallel workers (2-8)

AUDIO_PROMPT_PATH = "sample.wav" # Your voice sample
EXAGGERATION = 0.3              # Expressiveness (0.0-1.0)
CFG_WEIGHT = 0.9                # Voice faithfulness (0.0-1.0)

INPUT_FOLDER = "input_texts"    # Input directory
OUTPUT_FOLDER = "output_audio"  # Output directory
```

## Tips for Best Results

### Voice Sample
- **Duration:** 10-15 seconds ideal
- **Quality:** Clear, no background noise
- **Content:** Natural speech, full sentences
- **Format:** WAV preferred (16kHz+)

### Text Files
- **Size:** Split very long documents (> 5000 words) into multiple files
- **Format:** Plain text (.txt), UTF-8 encoding
- **Content:** Normal punctuation helps with prosody

### Performance
- **Speed:** Higher `MAX_PARALLEL_CHUNKS` = faster (more RAM)
- **Quality:** Higher `CFG_WEIGHT` = more consistent voice
- **Natural:** Lower `EXAGGERATION` (0.2-0.3) for neutral speech

## Help

Still stuck? Check:
1. Main [README.md](README.md) - Setup and installation
2. [BATCH_PROCESSOR_README.md](BATCH_PROCESSOR_README.md) - Detailed documentation
3. Run test script: `uv run test_text_processing.py`

Happy TTS processing! 🎙️
