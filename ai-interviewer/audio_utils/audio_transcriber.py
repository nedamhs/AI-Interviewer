import sounddevice as sd
import numpy as np
import queue
import threading
from faster_whisper import WhisperModel
import datetime
import webrtcvad

# ----- PRE-REQUISITES -----:
# NEED TO INSTALL BLACKHOLE AUDIO DRIVER OR OS COMPATIBLE VIRTUAL AUDIO DEVICE
# NEED TO INSTALL FFMPEG

SAMPLE_RATE = 16000 # samples taken per second for speech recognition
BLOCK_DURATION = 0.03
CHANNELS = 1 # BlackHole provides 2 input channels
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
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # Aggressive mode
        self.speech_buffer = []
        self.speech_detected = False
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
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            callback=self.audio_callback,
            device=0 # BlackHole index
        )
        self.stream.start()
        print("DEVICES: ", sd.query_devices()) # debug print
        # for idx, device in enumerate(sd.query_devices()):
        #     print(f"{idx}: {device['name']} - Input Channels: {device['max_input_channels']}, Output Channels: {device['max_output_channels']}")
        

    def transcribe_audio(self) -> None:
        """ Transcribe audio from the audio queue and into transcription queue 
            and write to transcription file."""
        print("Ready to transcribe...")
        buffer = np.empty((0, self.channels), dtype=np.int16)

        # Gathers audio
        while self.running:
            try:
                # get audio data from the queue
                data = self.audio_queue.get()
                buffer = np.concatenate((buffer, data), axis=0)
                
                # process the buffer if it has enough data
                block_size = int(self.sample_rate * self.block_duration)
                if buffer.shape[0] >= block_size:
                    chunk = buffer[:block_size]
                    buffer = buffer[block_size:]

                    # Check if block contains speech
                    is_speech = self.vad.is_speech(chunk.tobytes(), self.sample_rate)
                    if is_speech:
                        self.speech_buffer.append(chunk)
                        self.speech_detected = True
                        silence_duration = 0
                    elif self.speech_detected:
                        # add 2 second silence detection
                        silence_duration += self.block_duration
                        self.process_speech()
                        if silence_duration >= 2:
                            # Process the buffered speech
                            self.process_speech()
                            self.speech_detected = False
                            silence_duration = 0

            except Exception as e:
                print("Error during transcription:", e)

    def process_speech(self) -> None:
        """ Process buffered speech and transcribes into queue and file. """
        if not self.speech_buffer:
            return
        speech_data = np.concatenate(self.speech_buffer, axis=0) # concatenation off all chunks
        self.speech_buffer = [] # empty buffer for new input

        # Convert to float and mono for transcribe func
        audio_float = speech_data.astype(np.float32) / 32768.0
        audio_mono = audio_float.mean(axis=1)

        # print(f"Processing {len(audio_mono)} samples...") # debug print
        segments, _ = self.model.transcribe(audio_mono, language="en")

        # Currently writing to transcript file & queue
        with open(self.transcript_file, "a") as f:
            for segment in segments:
                timestamp = f"[{segment.start:.2f}s - {segment.end:.2f}s]"
                line = f"{timestamp}: {segment.text.strip()}"
                # print(line) # debug print
                f.write(line + "\n")
                self.transcript_queue.put(segment.text.strip())
                print("Speech ended...processing...")


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


if __name__=="__main__":
    transcriber = Transcriber()
    transcriber.transcribe_start()
    while True:
        print("Starting transcriber...", end='\n', flush=True)
        user_input = transcriber.transcript_queue.get()
        print(f"User: {user_input}")
        # print("BLAHBLAHBLAH...")
        # import time
        # time.sleep(2)
        print()
