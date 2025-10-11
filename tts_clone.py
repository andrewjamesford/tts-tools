import torch
import torchaudio as ta
import perth
from chatterbox.tts import ChatterboxTTS

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
# Use DummyWatermarker as a workaround
if perth.PerthImplicitWatermarker is None:
    perth.PerthImplicitWatermarker = perth.DummyWatermarker

model = ChatterboxTTS.from_pretrained(device=device)

# New Zealand accent example
text = "Today is the day. I want to move like a titan at dawn, sweat like a god forging lightning. No more excuses. From now on, my mornings will be temples of discipline. I am going to work out like the gods… every damn day."

# The model will clone the accent and voice characteristics from this file
AUDIO_PROMPT_PATH = "sample03.mp3"

# Adjust exaggeration and cfg_weight for different effects:
# - exaggeration: 0.0 (neutral) to 1.0 (more expressive)
# - cfg_weight: 0.0 (more creative) to 1.0 (more faithful to prompt)
wav = model.generate(
    text,
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.3,  # Lower for more natural speech
    cfg_weight=0.9,  # Higher to stay closer to the voice sample
)

ta.save("output_nz_accent.wav", wav, model.sr)
print(f"Generated audio with New Zealand accent saved to: output_nz_accent.wav")
