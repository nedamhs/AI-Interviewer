import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel
import datetime

# ----- PRE-REQUISITES -----:
# NEED TO INSTALL BLACKHOLE AUDIO DRIVER OR OS COMPATIBLE VIRTUAL AUDIO DEVICE
# NEED TO INSTALL FFMPEG

SAMPLE_RATE = 16000
BLOCK_DURATION = 4
CHANNELS = 2  # BlackHole provides 2 input channels
TRANSCRIPT_FILE = "transcript.txt" 



# record STT in real-time with the 5 second block
# record the audio continuously for full transcription

# current model being used
model = WhisperModel("tiny.en", compute_type="int8")
audio_queue = queue.Queue()


with open(TRANSCRIPT_FILE, "w") as f:
    f.write(f"Zoom Meeting Transcription Log\n{datetime.datetime.now()}\n\n")

def audio_callback(indata, frames, time, status) -> None:
    """"Callback function to handle audio input stream."""
    if status:
        print("Audio status:", status)
    audio_queue.put(indata.copy())


def start_audio_stream() -> sd.InputStream:
    """Start the audio input stream, returns the stream object."""

    print("Starting audio stream...")
    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16',
        callback=audio_callback,
        device=1  # BlackHole index
    )
    stream.start()
    return stream

def transcribe_audio() -> None:
    """ Transcribe audio from the queue and write to file."""
    print("Ready to transcribe...")
    buffer = np.empty((0, CHANNELS), dtype=np.int16)

    while True:
        try:
            # get audio data from the queue
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data), axis=0)

            # process the buffer if it has enough data
            if buffer.shape[0] >= SAMPLE_RATE * BLOCK_DURATION:
                chunk = buffer[:SAMPLE_RATE * BLOCK_DURATION]
                buffer = buffer[SAMPLE_RATE * BLOCK_DURATION:]

                # Convert to float and mono for transcribe func
                audio_float = chunk.astype(np.float32) / 32768.0
                audio_mono = audio_float.mean(axis=1)

                print(f"Processing {len(audio_mono)} samples...")
                segments, _ = model.transcribe(audio_mono, language="en")

                # currently writing to transcript file but need to route it to the interviewer, use a queue maybe?
                with open(TRANSCRIPT_FILE, "a") as f:
                    for segment in segments:
                        timestamp = f"[{segment.start:.2f}s - {segment.end:.2f}s]"
                        line = f"{timestamp}: {segment.text.strip()}"
                        print(line)
                        f.write(line + "\n")

        except Exception as e:
            print("Error during transcription:", e)

threading.Thread(target=transcribe_audio, daemon=True).start()
stream = start_audio_stream()

print("Listening... Ctrl+C to stop.")
try:
    while True:
        sd.sleep(100)
except KeyboardInterrupt:
    print("\nStopped.")

