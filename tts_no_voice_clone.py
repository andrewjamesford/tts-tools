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

# Generate without voice cloning (uses model's default voice)
text = "Today is the day. I want to move like a titan at dawn, sweat like a god forging lightning. No more excuses. From now on, my mornings will be temples of discipline. I am going to work out like the gods… every damn day."

# No audio_prompt_path means use the default voice
# Note: The default voice will likely have an American accent
wav = model.generate(text, exaggeration=0.5, cfg_weight=0.5)

ta.save("output_default_voice.wav", wav, model.sr)
print(f"Generated audio with default voice saved to: output_default_voice.wav")
