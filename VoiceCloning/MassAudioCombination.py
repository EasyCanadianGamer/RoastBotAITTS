from pydub import AudioSegment
import glob

# List all MP3 files in a folder (adjust path as needed)
mp3_files = sorted(glob.glob("*.mp3"))

# Load and concatenate all MP3s
combined = AudioSegment.empty()
for file in mp3_files:
    audio = AudioSegment.from_mp3(file)
    combined += audio

# Export as a single MP3
combined.export("combined_audio.mp3", format="mp3")

# Convert to WAV
combined.export("combined_audio.wav", format="wav")
