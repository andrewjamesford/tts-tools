import torch
import torchaudio as ta
import perth
from chatterbox.tts import ChatterboxTTS
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# ============================================================================
# CONFIGURATION
# ============================================================================

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
INPUT_FOLDER = "input_texts"  # Folder containing .txt files
OUTPUT_FOLDER = "output_audio"  # Where to save generated audio


# ============================================================================
# TEXT NORMALIZATION
# ============================================================================

# Acronym dictionary for pronunciation
ACRONYMS = {
    # Storage units
    r"\bGB\b": "gigabyte",
    r"\bGBs\b": "gigabytes",
    r"\bTB\b": "terabyte",
    r"\bTBs\b": "terabytes",
    r"\bMB\b": "megabyte",
    r"\bMBs\b": "megabytes",
    r"\bKB\b": "kilobyte",
    r"\bKBs\b": "kilobytes",
    r"\bPB\b": "petabyte",
    r"\bPBs\b": "petabytes",
    # Hardware
    r"\bSSD\b": "S S D",
    r"\bHDD\b": "H D D",
    r"\bCPU\b": "C P U",
    r"\bGPU\b": "G P U",
    r"\bRAM\b": "R A M",
    r"\bUSB\b": "U S B",
    r"\bHDMI\b": "H D M I",
    # Common tech acronyms
    r"\bAPI\b": "A P I",
    r"\bURL\b": "U R L",
    r"\bHTML\b": "H T M L",
    r"\bCSS\b": "C S S",
    r"\bJSON\b": "J S O N",
    r"\bXML\b": "X M L",
    r"\bSQL\b": "S Q L",
    r"\bAI\b": "A I",
    r"\bML\b": "M L",
    r"\bVPN\b": "V P N",
    r"\bWiFi\b": "Wi-Fi",
    r"\bWi-Fi\b": "Wi-Fi",
    # Business
    r"\bCEO\b": "C E O",
    r"\bCTO\b": "C T O",
    r"\bCFO\b": "C F O",
    r"\bHR\b": "H R",
    r"\bPR\b": "P R",
    r"\bSEO\b": "S E O",
    # General
    r"\bUS\b": "U S",
    r"\bUK\b": "U K",
    r"\bNZ\b": "N Z",
    r"\bAU\b": "A U",
    r"\bEU\b": "E U",
    r"\bPDF\b": "P D F",
    r"\bFAQ\b": "F A Q",
    r"\bETA\b": "E T A",
    r"\bASAP\b": "A S A P",
}


def convert_acronyms(text: str) -> str:
    """Convert acronyms to their pronounceable forms."""
    for pattern, replacement in ACRONYMS.items():
        text = re.sub(pattern, replacement, text)
    return text


def number_to_words(num_str: str) -> str:
    """Convert numbers to words for better TTS pronunciation."""
    ones = [
        "zero",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
    ]
    teens = [
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ]
    tens = [
        "",
        "",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
    ]

    try:
        num = int(num_str)

        if num < 10:
            return ones[num]
        elif num < 20:
            return teens[num - 10]
        elif num < 100:
            ten_digit = num // 10
            one_digit = num % 10
            if one_digit == 0:
                return tens[ten_digit]
            return f"{tens[ten_digit]} {ones[one_digit]}"
        elif num < 1000:
            hundred_digit = num // 100
            remainder = num % 100
            result = f"{ones[hundred_digit]} hundred"
            if remainder > 0:
                result += f" and {number_to_words(str(remainder))}"
            return result
        else:
            # For larger numbers, just read digit by digit
            return " ".join(ones[int(d)] for d in num_str)
    except:
        return num_str


def convert_numbers_and_decimals(text: str) -> str:
    """Convert numbers and decimals to words."""

    # Handle decimals (e.g., 1.66 -> one point six six)
    def decimal_to_words(match):
        number = match.group(0)
        parts = number.split(".")

        integer_part = number_to_words(parts[0])

        if len(parts) > 1:
            decimal_digits = " ".join(number_to_words(d) for d in parts[1])
            return f"{integer_part} point {decimal_digits}"
        return integer_part

    # Match decimal numbers (including optional negative sign)
    text = re.sub(r"-?\d+\.\d+", decimal_to_words, text)

    # Match whole numbers (but not years like 2024 or IDs)
    # Only convert standalone numbers under 10000
    def whole_number_to_words(match):
        num = match.group(0)
        if len(num) <= 3 or int(num) < 100:
            return number_to_words(num)
        return num  # Keep larger numbers as-is (likely years, IDs, etc.)

    text = re.sub(r"\b\d{1,3}\b", whole_number_to_words, text)

    return text


def normalize_text(text: str) -> str:
    """Apply all text normalizations for better TTS."""
    # First handle number+acronym combinations (e.g., 512GB -> 512 gigabytes)
    storage_units = [
        (r"(\d+)\s*GB\b", r"\1 gigabyte"),
        (r"(\d+)\s*TB\b", r"\1 terabyte"),
        (r"(\d+)\s*MB\b", r"\1 megabyte"),
        (r"(\d+)\s*KB\b", r"\1 kilobyte"),
        (r"(\d+)\s*PB\b", r"\1 petabyte"),
    ]
    for pattern, replacement in storage_units:
        text = re.sub(pattern, replacement, text)

    # Then convert other acronyms
    text = convert_acronyms(text)

    # Finally convert numbers to words
    text = convert_numbers_and_decimals(text)
    return text


# ============================================================================
# SENTENCE PROCESSING
# ============================================================================


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using multiple delimiters."""
    # Split on common sentence endings
    sentences = re.split(r"[.!?]+\s+", text)

    # Clean up and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]

    return sentences


def split_long_sentence(
    sentence: str, max_length: int = LONG_SENTENCE_THRESHOLD
) -> List[str]:
    """Recursively split long sentences at natural break points."""
    if len(sentence) <= max_length:
        return [sentence]

    # Try to split at natural break points in order of preference
    break_chars = [";", ":", " - ", ","]

    for char in break_chars:
        if char in sentence:
            # Find the best split point near the middle
            mid_point = len(sentence) // 2
            positions = [
                i for i, c in enumerate(sentence) if sentence[i : i + len(char)] == char
            ]

            if positions:
                # Find position closest to middle
                best_pos = min(positions, key=lambda x: abs(x - mid_point))

                left = sentence[:best_pos].strip()
                right = sentence[best_pos + len(char) :].strip()

                # Recursively split if still too long
                return split_long_sentence(left, max_length) + split_long_sentence(
                    right, max_length
                )

    # If no natural break point, split by character count at last space
    if " " in sentence:
        split_pos = sentence.rfind(" ", 0, max_length)
        if split_pos > 0:
            left = sentence[:split_pos].strip()
            right = sentence[split_pos:].strip()
            return split_long_sentence(left, max_length) + split_long_sentence(
                right, max_length
            )

    # Last resort: just return the sentence
    return [sentence]


def merge_short_sentences(
    sentences: List[str], min_length: int = MIN_SENTENCE_LENGTH
) -> List[str]:
    """Merge very short sentences for smoother prosody."""
    if not sentences:
        return []

    merged = []
    current = sentences[0]

    for i in range(1, len(sentences)):
        if len(current) < min_length:
            current = f"{current} {sentences[i]}"
        else:
            merged.append(current)
            current = sentences[i]

    merged.append(current)
    return merged


def batch_sentences(
    sentences: List[str], target_size: int = BATCH_SIZE_CHARS
) -> List[str]:
    """Group sentences into chunks of approximately target_size characters."""
    if not sentences:
        return []

    batches = []
    current_batch = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        # If adding this sentence would exceed target, start a new batch
        if current_batch and (current_length + sentence_length > target_size):
            batches.append(" ".join(current_batch))
            current_batch = []
            current_length = 0

        current_batch.append(sentence)
        current_length += sentence_length

    # Add the last batch
    if current_batch:
        batches.append(" ".join(current_batch))

    return batches


def process_text_into_chunks(text: str) -> List[str]:
    """Process text into optimized chunks for TTS generation."""
    # Normalize the text
    text = normalize_text(text)

    # Split into sentences
    sentences = split_into_sentences(text)

    # Split long sentences recursively
    processed_sentences = []
    for sentence in sentences:
        processed_sentences.extend(split_long_sentence(sentence))

    # Apply batching or merging based on configuration
    if ENABLE_BATCHING:
        chunks = batch_sentences(processed_sentences, BATCH_SIZE_CHARS)
    else:
        chunks = merge_short_sentences(processed_sentences, MIN_SENTENCE_LENGTH)

    return chunks


# ============================================================================
# TTS GENERATION
# ============================================================================

# Thread-safe model initialization
_model = None
_model_lock = threading.Lock()


def get_model():
    """Get or initialize the TTS model (thread-safe singleton)."""
    global _model

    if _model is None:
        with _model_lock:
            if _model is None:  # Double-check locking
                # Detect device (Mac with M1/M2/M3/M4)
                device = "mps" if torch.backends.mps.is_available() else "cpu"
                map_location = torch.device(device)

                torch_load_original = torch.load

                def patched_torch_load(*args, **kwargs):
                    if "map_location" not in kwargs:
                        kwargs["map_location"] = map_location
                    return torch_load_original(*args, **kwargs)

                torch.load = patched_torch_load

                # Fix for PerthImplicitWatermarker being None in resemble-perth 1.0.1
                if perth.PerthImplicitWatermarker is None:
                    perth.PerthImplicitWatermarker = perth.DummyWatermarker

                _model = ChatterboxTTS.from_pretrained(device=device)
                print(f"TTS model loaded on device: {device}")

    return _model


def generate_audio_for_chunk(
    chunk: str, chunk_index: int, output_base: str, timestamp: str
) -> str:
    """Generate audio for a single chunk."""
    model = get_model()

    try:
        wav = model.generate(
            chunk,
            audio_prompt_path=AUDIO_PROMPT_PATH,
            exaggeration=EXAGGERATION,
            cfg_weight=CFG_WEIGHT,
        )

        # Create output filename with numbering and timestamp
        output_path = f"{output_base}_{chunk_index:02d}_{timestamp}.wav"
        ta.save(output_path, wav, model.sr)

        print(f"  ✓ Generated chunk {chunk_index:02d}: {output_path}")
        return output_path
    except Exception as e:
        print(f"  ✗ Error generating chunk {chunk_index:02d}: {e}")
        return None


def generate_audio_parallel(
    chunks: List[str], output_base: str, timestamp: str
) -> List[str]:
    """Generate audio for multiple chunks in parallel."""
    output_files = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_CHUNKS) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(
                generate_audio_for_chunk, chunk, i, output_base, timestamp
            ): i
            for i, chunk in enumerate(chunks)
        }

        # Collect results as they complete
        results = {}
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            results[index] = future.result()

        # Sort by index to maintain order
        output_files = [results[i] for i in sorted(results.keys())]

    return output_files


# ============================================================================
# FILE PROCESSING
# ============================================================================


def process_text_file(input_path: Path) -> None:
    """Process a single text file and generate audio chunks."""
    print(f"\n{'=' * 80}")
    print(f"Processing: {input_path.name}")
    print(f"{'=' * 80}")

    # Read the input file
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if not text:
        print("File is empty, skipping...")
        return

    # Process text into chunks
    print("Processing text into chunks...")
    chunks = process_text_into_chunks(text)
    print(f"Created {len(chunks)} chunks")

    # Show chunk preview
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i:02d} ({len(chunk)} chars): {chunk[:80]}...")

    # Create output filename base
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    output_base = Path(OUTPUT_FOLDER) / input_path.stem

    # Generate audio for all chunks
    print(f"\nGenerating audio (using {MAX_PARALLEL_CHUNKS} parallel workers)...")
    output_files = generate_audio_parallel(chunks, str(output_base), timestamp)

    # Summary
    successful = [f for f in output_files if f is not None]
    print(f"\n✓ Completed: {len(successful)}/{len(chunks)} chunks generated")
    print(f"  Output files: {OUTPUT_FOLDER}/")


def process_all_text_files():
    """Process all text files in the input folder."""
    # Create directories if they don't exist
    input_dir = Path(INPUT_FOLDER)
    output_dir = Path(OUTPUT_FOLDER)

    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Find all .txt files
    txt_files = list(input_dir.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in {INPUT_FOLDER}/")
        print(f"Please add text files to process.")
        return

    print(f"\n{'=' * 80}")
    print(f"TTS BATCH PROCESSOR")
    print(f"{'=' * 80}")
    print(f"Configuration:")
    print(f"  Batching: {'Enabled' if ENABLE_BATCHING else 'Disabled'}")
    print(f"  Batch size: {BATCH_SIZE_CHARS} characters")
    print(f"  Parallel workers: {MAX_PARALLEL_CHUNKS}")
    print(f"  Voice sample: {AUDIO_PROMPT_PATH}")
    print(f"  Found {len(txt_files)} text file(s)")
    print(f"{'=' * 80}")

    # Process each file
    for txt_file in txt_files:
        process_text_file(txt_file)

    print(f"\n{'=' * 80}")
    print(f"ALL FILES PROCESSED")
    print(f"{'=' * 80}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    process_all_text_files()
