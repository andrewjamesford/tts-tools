# TTS Batch Processor

A powerful batch processing tool for converting multiple text files into high-quality speech audio with intelligent text normalization, sentence batching, and parallel processing.

## Features

### 📝 Text Processing
- **Sentence Batching**: Groups sentences up to ~300 characters per chunk (configurable)
- **Smart Short Sentence Merging**: Combines very short sentences for smoother prosody when batching is disabled
- **Recursive Long Sentence Splitting**: Automatically splits sentences longer than 500 characters at natural break points (`;`, `:`, `-`, `,`)
- **Parallel Chunk Processing**: Generates multiple audio chunks simultaneously for faster processing

### 🔤 Text Normalization
- **Acronym Conversion**: Automatically converts acronyms for proper pronunciation
  - Storage: GB → gigabyte, TB → terabyte, SSD → S S D
  - Hardware: CPU → C P U, GPU → G P U, RAM → R A M
  - Tech: API → A P I, URL → U R L, JSON → J S O N
  - And many more...
  
- **Number to Words**: Converts numbers and decimals for natural speech
  - `1.66` → "one point six six"
  - `25` → "twenty five"
  - `4.8` → "four point eight"

### 📁 File Management
- **Batch Processing**: Processes all `.txt` files in the input folder
- **Smart Output Naming**: Files are named with original name + chunk number + timestamp
  - Example: `TextFile01.txt` produces:
    - `TextFile01_00_20251012-1302.wav`
    - `TextFile01_01_20251012-1302.wav`
    - `TextFile01_02_20251012-1302.wav`

## Installation

Ensure you have the base TTS tools installed (see main README.md).

## Configuration

Edit the configuration section at the top of `tts_batch_processor.py`:

```python
# Sentence batching settings
ENABLE_BATCHING = True
BATCH_SIZE_CHARS = 300  # Target characters per chunk
MIN_SENTENCE_LENGTH = 30  # Merge sentences shorter than this when batching is off
LONG_SENTENCE_THRESHOLD = 500  # Split sentences longer than this

# Parallel processing
MAX_PARALLEL_CHUNKS = 4  # Number of chunks to process simultaneously

# Audio generation settings
AUDIO_PROMPT_PATH = "sample03.mp3"  # Voice to clone
EXAGGERATION = 0.3  # 0.0 (neutral) to 1.0 (expressive)
CFG_WEIGHT = 0.9  # 0.0 (creative) to 1.0 (faithful to prompt)

# Input/Output directories
INPUT_FOLDER = "input_texts"
OUTPUT_FOLDER = "output_audio"
```

### Configuration Options Explained

#### Sentence Batching
- **ENABLE_BATCHING**: When `True`, groups sentences into chunks. When `False`, processes sentences individually with smart merging
- **BATCH_SIZE_CHARS**: Target size for each chunk (default 300 chars ≈ 2-3 sentences)
- **MIN_SENTENCE_LENGTH**: Minimum length before merging short sentences together
- **LONG_SENTENCE_THRESHOLD**: Maximum sentence length before automatic splitting

#### Parallel Processing
- **MAX_PARALLEL_CHUNKS**: How many audio chunks to generate simultaneously
  - Higher = faster processing but more memory usage
  - Recommended: 2-4 for most systems
  - Adjust based on your hardware capabilities

#### Audio Settings
- **AUDIO_PROMPT_PATH**: Path to the voice sample file to clone
- **EXAGGERATION**: Controls emotional expression (0.0 = neutral, 1.0 = very expressive)
- **CFG_WEIGHT**: Controls faithfulness to voice sample (0.0 = creative, 1.0 = faithful)

## Usage

### 1. Prepare Your Text Files

Place your `.txt` files in the `input_texts/` folder:

```bash
input_texts/
├── chapter01.txt
├── article.txt
└── story.txt
```

### 2. Set Your Voice Sample

Update `AUDIO_PROMPT_PATH` to point to your voice sample file:

```python
AUDIO_PROMPT_PATH = "my_voice_sample.wav"
```

### 3. Run the Processor

```bash
uv run tts_batch_processor.py
```

### 4. Check Output

Generated audio files will be in the `output_audio/` folder:

```bash
output_audio/
├── chapter01_00_20251012-1345.wav
├── chapter01_01_20251012-1345.wav
├── chapter01_02_20251012-1345.wav
├── article_00_20251012-1345.wav
└── article_01_20251012-1345.wav
```

## How It Works

### Text Processing Pipeline

1. **Load Text File**: Reads the entire text file
2. **Normalize Text**: 
   - Converts acronyms (GB → gigabyte)
   - Converts numbers to words (1.66 → one point six six)
3. **Split into Sentences**: Uses punctuation to identify sentence boundaries
4. **Split Long Sentences**: Recursively splits sentences > 500 chars at natural break points
5. **Batch or Merge**:
   - If batching enabled: Groups sentences up to ~300 chars
   - If batching disabled: Merges short sentences together
6. **Generate Audio**: Processes chunks in parallel using thread pool
7. **Save Files**: Saves each chunk with numbered filename and timestamp

### Sentence Splitting Logic

The processor intelligently splits long sentences at natural break points in this priority order:

1. Semicolon (`;`)
2. Colon (`:`)
3. Dash (` - `)
4. Comma (`,`)
5. Space (at max length boundary)

This ensures the audio maintains natural prosody and phrasing.

### Text Normalization Examples

| Input | Output |
|-------|--------|
| "The SSD has 512GB storage" | "The S S D has five hundred twelve gigabyte storage" |
| "The API returns JSON data" | "The A P I returns J S O N data" |
| "CPU and GPU performance" | "C P U and G P U performance" |
| "Price is 1299.99" | "Price is one thousand two hundred ninety nine point nine nine" |
| "It takes 8.5 seconds" | "It takes eight point five seconds" |
| "The CEO and CTO met" | "The C E O and C T O met" |

## Performance Tips

### Optimize for Speed
- Increase `MAX_PARALLEL_CHUNKS` (4-8 on powerful machines)
- Enable batching to reduce total number of chunks
- Use shorter text files (split very long documents)

### Optimize for Quality
- Reduce `MAX_PARALLEL_CHUNKS` (1-2) to reduce memory pressure
- Use higher `CFG_WEIGHT` (0.8-1.0) for more consistent voice
- Disable batching for more control over sentence breaks

### Memory Management
- If you encounter memory errors, reduce `MAX_PARALLEL_CHUNKS`
- Process fewer files at a time
- Close other applications while processing

## Customizing Acronyms

To add your own acronyms, edit the `ACRONYMS` dictionary in `tts_batch_processor.py`:

```python
ACRONYMS = {
    r'\bYOUR_ACRONYM\b': 'pronunciation',
    r'\bNASA\b': 'N A S A',
    r'\bSaaS\b': 'Software as a Service',
    # Add more as needed
}
```

Use `\b` for word boundaries to match whole words only.

## Customizing Number Conversion

The `number_to_words()` function converts numbers intelligently:
- Small numbers (< 1000): Full word conversion
- Large numbers: Digit-by-digit reading
- Decimals: "point" separator with digit-by-digit decimals

Modify the function in the script if you need different behavior.

## Troubleshooting

### No Files Processed
- Check that `.txt` files exist in `input_texts/` folder
- Verify file permissions

### Audio Quality Issues
- Adjust `EXAGGERATION` (try 0.2-0.4 for more natural speech)
- Adjust `CFG_WEIGHT` (try 0.8-0.95 for more consistent voice)
- Check your voice sample quality (needs clear, clean audio)

### Memory Errors
- Reduce `MAX_PARALLEL_CHUNKS` to 1 or 2
- Process files individually
- Restart the script between files

### Slow Processing
- Increase `MAX_PARALLEL_CHUNKS`
- Enable batching to reduce total chunks
- Check if running on correct device (should use MPS on Mac)

### Incorrect Pronunciations
- Add specific words to the `ACRONYMS` dictionary
- Manually edit text files to spell out problematic words
- Use phonetic spellings in source text

## Example Output

Processing `example01.txt` (5 paragraphs, ~350 words):

```
================================================================================
Processing: example01.txt
================================================================================
Processing text into chunks...
Created 3 chunks
  Chunk 00 (285 chars): The new laptop comes with sixteen gigabyte of R A M and a five hundred...
  Chunk 01 (298 chars): For developers, the A P I documentation is available online. You can w...
  Chunk 02 (215 chars): The price is competitive at one thousand two hundred ninety nine point...

Generating audio (using 4 parallel workers)...
  ✓ Generated chunk 00: output_audio/example01_00_20251012-1430.wav
  ✓ Generated chunk 02: output_audio/example01_02_20251012-1430.wav
  ✓ Generated chunk 01: output_audio/example01_01_20251012-1430.wav

✓ Completed: 3/3 chunks generated
  Output files: output_audio/
```

## Advanced Usage

### Processing Specific Files

Modify the script to process specific files:

```python
# At the bottom of the script
if __name__ == "__main__":
    # Process only specific files
    process_text_file(Path("input_texts/chapter01.txt"))
```

### Changing Batch Strategy

You can implement custom batching logic by modifying the `batch_sentences()` function:

```python
def batch_sentences(sentences: List[str], target_size: int = BATCH_SIZE_CHARS) -> List[str]:
    # Your custom batching logic here
    pass
```

### Using Different Voice Samples Per File

Modify `process_text_file()` to accept a voice sample parameter:

```python
def process_text_file(input_path: Path, voice_sample: str = AUDIO_PROMPT_PATH):
    # Use the voice_sample parameter in generation
    pass
```

## Integration with Other Tools

### Combining Audio Files

Use `ffmpeg` to combine multiple chunks into a single file:

```bash
# Create a file list
ls output_audio/chapter01_*.wav | sed 's/^/file /' > filelist.txt

# Concatenate
ffmpeg -f concat -safe 0 -i filelist.txt -c copy chapter01_complete.wav
```

### Batch Convert to MP3

```bash
for f in output_audio/*.wav; do
    ffmpeg -i "$f" -codec:a libmp3lame -qscale:a 2 "${f%.wav}.mp3"
done
```

## License

Same as the main TTS Tools project (MIT License).

## Credits

Built on top of:
- ChatterboxTTS by Resemble AI
- PyTorch and TorchAudio
- Python standard library

## Support

For issues or questions:
1. Check this documentation
2. Review the main README.md
3. Check the ChatterboxTTS documentation
4. Open an issue on the repository
