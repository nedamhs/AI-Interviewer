from deepgram.utils import verboselogs
import os

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

import asyncio

class DeepgramTranscriber:
    def __init__(self, transcript_queue = None):
        # Configure the DeepgramClientOptions to enable KeepAlive for maintaining the WebSocket connection (only if necessary to your scenario)
        config = DeepgramClientOptions(
            options={"keepalive": "true"}
        )

        self.transcript_queue = transcript_queue

        # Create a websocket connection using the DEEPGRAM_API_KEY from environment variables
        self.deepgram = DeepgramClient(os.environ.get('DEEPGRAM_API_KEY'), config)

        # Use the listen.live class to create the websocket connection
        self.dg_connection = self.deepgram.listen.websocket.v("1") 

        def on_message(self, result, **kwargs):
            if hasattr(result, "speech_final") and result.speech_final:
                sentence = result.channel.alternatives[0].transcript
                print(f"🟢Final Transcription🟢: {sentence}")
                if self.transcript_queue:
                    self.transcript_queue.put(sentence)

        self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        def on_error(self, error, **kwargs):
            print(f"Error: {error}")

        self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-3",
            punctuate=True,
            interim_results=True,
            language='en-GB',
            encoding= "linear16",
            sample_rate=32000,
            endpointing=500
            
            )

        self.dg_connection.start(options)

    def send(self, data):
        self.dg_connection.send(data)

    def finish(self):
        self.dg_connection.finish()