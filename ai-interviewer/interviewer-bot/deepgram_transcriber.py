from deepgram.utils import verboselogs
import os

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from functools import partial

import asyncio

class DeepgramTranscriber:
    def __init__(self, transcript_queue=None):
        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.transcript_queue = transcript_queue
        self.deepgram = DeepgramClient(os.environ.get('DEEPGRAM_API_KEY'), config)
        self.dg_connection = self.deepgram.listen.websocket.v("1") 

        self.current_sentence = []

        # Hook up the event handlers
        self.dg_connection.on(LiveTranscriptionEvents.Transcript, partial(self._on_message))
        self.dg_connection.on(LiveTranscriptionEvents.Error, partial(self._on_error))

        options = LiveOptions(
            model="nova-3",
            # punctuate=True,
            interim_results=True,
            language='en-GB',
            encoding="linear16",
            sample_rate=32000,
            endpointing=1500
        )

        self.dg_connection.start(options)

    def trim_tail(self, prev: str, curr: str) -> str:
        prev_words = prev.split()
        curr_words = curr.split()
        overlap_max = 0
        for i in range(1, min(len(prev_words), len(curr_words)) + 1):
            if prev_words[-i:] == curr_words[:i]:
                overlap_max = i
        return " ".join(curr_words[overlap_max:])

    def _on_message(self, client, result, **kwargs):
        transcript = result.channel.alternatives[0].transcript

        if getattr(result, "is_final", False):
            cleaned = self.trim_tail(" ".join(self.current_sentence), transcript)
            self.current_sentence.append(cleaned)

            if getattr(result, "speech_final", False):
                full_utterance = " ".join(self.current_sentence).strip()
                print(f"🟢Final Transcription🟢: {full_utterance}")
                self.current_sentence.clear()
                if self.transcript_queue:
                    self.transcript_queue.put(full_utterance)

    def _on_error(self, client, error, **kwargs):
        print(f"Error: {error}")

    def send(self, data):
        self.dg_connection.send(data)

    def finish(self):
        self.dg_connection.finish()
