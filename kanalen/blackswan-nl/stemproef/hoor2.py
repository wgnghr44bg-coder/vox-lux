import soundfile as sf, librosa, torch, sys
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = librosa.load(sys.argv[1], sr=16000)
print(asr({"raw": a, "sampling_rate": 16000}, return_timestamps=True, generate_kwargs={"task": "transcribe", "language": "dutch"})["text"])
