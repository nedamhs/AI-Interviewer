import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from openai._response import AsyncStreamedBinaryAPIResponse
import sounddevice as sd
import os
import numpy as np
load_dotenv()
openai = AsyncOpenAI(api_key=os.environ.get("OPENAI-API-KEY"))
# Needs ffmpeg installed

#NEED TO SPECIFY
DEVICE = 1
RATE = 24000 
BLOCK_SIZE = 1024

async def text_to_audio(text: str) -> None:
  '''
  Creates an api stream to read a string

      Inputs:
        text: str 
            text to serve as the input to the bot.
      Returns: 
        None
  '''

  async with openai.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=text,
    response_format="pcm",
  ) as response:
    await asyncio.sleep(1) # Note: this is needed to buffer some audio to ensure a non static response
    await play_stream(response)

async def play_stream(audio_bytes:AsyncStreamedBinaryAPIResponse) -> None:
    '''
      Takes the audio, sets a device and streams the audio to the specific divice 

      Inputs:
        audio_bytes 
            async api bytes of audio 
      Returns: 
        None
    '''
    devinfo = sd.query_devices(DEVICE)
    out_channels = devinfo['max_output_channels'] 

    with sd.OutputStream(
        samplerate=RATE,
        blocksize= BLOCK_SIZE,
        channels=out_channels,
        dtype='int16',
        device=DEVICE,
    ) as stream:
        leftover = b""
        async for raw in audio_bytes.iter_bytes():
            data = leftover + raw
            if len(data) % 2:
                leftover = data[-1:]
                data = data[:-1]
            else:
                leftover = b""
            mono = np.frombuffer(data, dtype='<i2')
            if out_channels > 1:
                frames = mono.shape[0]
                stereo = np.repeat(mono.reshape(frames, 1), out_channels, axis=1)
                write_arr = stereo
            else:
                write_arr = mono
            stream.write(np.ascontiguousarray(write_arr))


if __name__ == "__main__":
   print(sd.query_devices())
   asyncio.run(text_to_audio("One last audio test to ensure that the text to speech is working properly!"))
