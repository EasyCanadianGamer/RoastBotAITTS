import torch
from TTS.api import TTS  


device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "tts_models/multilingual/multi-dataset/xtts_v2"

# Initialize TTS model
tts = TTS(model_name).to(device)



speaker_id = "Asuka"

# Step 1: Create and cache speaker embedding if it doesn't exist
wav_path = "Asuka.wav"  # reference voice sample
tts.tts_to_file(
        text="Shinji, you are such a baka!",
        file_path="asuka_clone.wav",
        speaker_wav=wav_path,
        speaker=speaker_id,
        language="en"
    )


# Step 3: Reuse the cloned voice without reference audio
tts.tts_to_file(
    text="This is the cloned voice again!",
    file_path="asuka_clone_2.wav",
    speaker=speaker_id,
    language="en"
)
