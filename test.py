# Record Some audio

import wave
import sys
import pyaudio
import whisper

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == "darwin" else 2
RATE = 44100


def record_audio(seconds: int):
    output_path = "test.wav"
    with wave.open(output_path, "wb") as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)

        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)

        print("Recording...")
        for index in range(0, RATE // CHUNK * seconds):
            if index % (RATE // CHUNK) == 0:
                print(f"{index // (RATE // CHUNK)} / {seconds}s")
            wf.writeframes(stream.read(CHUNK))
        print("Done")

        stream.close()
        p.terminate()
    print(f"File saved at {output_path}")
    return output_path

record_audio(10)



model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio = whisper.load_audio("test.wav")
audio = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode the audio
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

# print the recognized text
print(result.text)