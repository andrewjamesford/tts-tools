"""
Test script to validate text processing without running TTS generation.
This helps verify the batching, normalization, and splitting logic.
"""

from pathlib import Path
from tts_batch_processor import (
    process_text_into_chunks,
    normalize_text,
    convert_acronyms,
    convert_numbers_and_decimals,
)


def test_file(file_path: Path):
    """Test processing a single file and show the results."""
    print(f"\n{'=' * 80}")
    print(f"Testing: {file_path.name}")
    print(f"{'=' * 80}")

    # Read file
    with open(file_path, "r", encoding="utf-8") as f:
        original_text = f.read().strip()

    print(f"\nOriginal text length: {len(original_text)} characters")
    print(f"\nFirst 200 chars: {original_text[:200]}...")

    # Process into chunks
    chunks = process_text_into_chunks(original_text)

    print(f"\n{'=' * 80}")
    print(f"Generated {len(chunks)} chunks:")
    print(f"{'=' * 80}")

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i:02d} ({len(chunk)} chars) ---")
        print(chunk)
        print(f"--- End Chunk {i:02d} ---")

    return chunks


def test_normalization():
    """Test text normalization functions."""
    print(f"\n{'=' * 80}")
    print("Testing Text Normalization")
    print(f"{'=' * 80}")

    test_cases = [
        "The SSD has 512GB storage and 16GB RAM.",
        "The API returns JSON data with CPU usage at 25%.",
        "Price is 1299.99 for the laptop.",
        "It takes 8.5 seconds to boot with NZ wifi.",
        "The CEO and CTO met with HR about AI and ML.",
        "Download speed: 1.66 GB per second via USB.",
    ]

    for text in test_cases:
        normalized = normalize_text(text)
        print(f"\nOriginal:   {text}")
        print(f"Normalized: {normalized}")


if __name__ == "__main__":
    print("=" * 80)
    print("TTS BATCH PROCESSOR - TEXT PROCESSING TEST")
    print("=" * 80)

    # Test normalization
    test_normalization()

    # Test file processing
    input_dir = Path("input_texts")
    txt_files = list(input_dir.glob("*.txt"))

    if not txt_files:
        print("\nNo text files found in input_texts/")
    else:
        for txt_file in txt_files:
            test_file(txt_file)

    print(f"\n{'=' * 80}")
    print("Testing Complete!")
    print(f"{'=' * 80}")
