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
CHANNELS = 1  # BlackHole provides 2 input channels
TRANSCRIPT_FILE = "transcript.txt" 


# record STT in real-time with the 5 second block
# record the audio continuously for full transcription

class Transcriber:
    def __init__(self, sample_rate=SAMPLE_RATE, block_duration=BLOCK_DURATION, channels=CHANNELS, transcript_file=TRANSCRIPT_FILE,
                 model_name="tiny.en", compute_type="int8"):
        self.sample_rate = sample_rate
        self.block_duration = block_duration
        self.channels = channels
        self.transcript_file = transcript_file
        # current model being used
        self.model = WhisperModel(model_name, compute_type=compute_type)
        self.stream = None
        self.running = False
        self.thread = None

        self.audio_queue = queue.Queue()
        self.transcript_queue = queue.Queue()
        with open(TRANSCRIPT_FILE, "w") as f:
            f.write(f"Zoom Meeting Transcription Log\n{datetime.datetime.now()}\n\n")

    def audio_callback(self, indata, frames, time, status) -> None:
        """"Callback function to handle audio input stream."""
        if status:
            print("Audio status:", status)
        self.audio_queue.put(indata.copy())


    def start_audio_stream(self) -> None:
        """Start the audio input stream"""

        print("Starting audio stream...")
        print("DEVICES: ", sd.query_devices())
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            callback=self.audio_callback,
            device=1  # BlackHole index
        )
        self.stream.start()
        

    def transcribe_audio(self) -> None:
        """ Transcribe audio from the queue and write to file."""
        print("Ready to transcribe...")
        buffer = np.empty((0, self.channels), dtype=np.int16)

        while self.running:
            try:
                # get audio data from the queue
                data = self.audio_queue.get()
                buffer = np.concatenate((buffer, data), axis=0)
                
                # process the buffer if it has enough data
                if buffer.shape[0] >= self.sample_rate * self.block_duration:
                    chunk = buffer[:self.sample_rate * self.block_duration]
                    buffer = buffer[self.sample_rate * self.block_duration:]

                    # Convert to float and mono for transcribe func
                    audio_float = chunk.astype(np.float32) / 32768.0
                    audio_mono = audio_float.mean(axis=1)

                    # print(f"Processing {len(audio_mono)} samples...") # debug print
                    segments, _ = self.model.transcribe(audio_mono, language="en")

                    # currently writing to transcript file & queue
                    with open(self.transcript_file, "a") as f:
                        for segment in segments:
                            timestamp = f"[{segment.start:.2f}s - {segment.end:.2f}s]"
                            line = f"{timestamp}: {segment.text.strip()}"
                            # print(line) # debug print
                            f.write(line + "\n")
                            self.transcript_queue.put(segment.text.strip())

            except Exception as e:
                print("Error during transcription:", e)

    def transcribe_start(self) -> None:
        """ Starts transriber, starting the thread and audio stream. """
        self.running = True
        self.thread = threading.Thread(target=self.transcribe_audio, daemon=True).start()
        self.start_audio_stream()
        print("Listening... Ctrl+C to stop.")

    def transcribe_stop(self) -> None:
        """ Stops transcriber. """
        self.running = False
        if self.thread:
            self.thread.join()
        if self.stream:
            self.stream.stop()
            self.stream.close()
