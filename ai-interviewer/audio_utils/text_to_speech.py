import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from openai._response import AsyncStreamedBinaryAPIResponse
import os
import numpy as np
from scipy.signal import resample_poly
load_dotenv()
openai = AsyncOpenAI(api_key=os.environ.get("OPENAI-API-KEY"))


#NEED TO SPECIFY
RATE = 24000 
BLOCK_SIZE = 256

def resample_pcm_24k_to_32k(pcm_bytes: bytes) -> bytes:
    audio_24k = np.frombuffer(pcm_bytes, dtype='<i2')  # little-endian 16-bit PCM

    audio_32k = resample_poly(audio_24k, up=4, down=3)

    audio_32k = np.clip(audio_32k, -32768, 32767).astype('<i2')

    return audio_32k.tobytes()

async def text_to_audio(text: str,callback: callable) -> None:
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
    await play_stream(response, callback)

async def play_stream(audio_bytes:AsyncStreamedBinaryAPIResponse, callback:callable) -> None:
    '''
      Takes the audio, sets a device and streams the audio to the specific divice 

      Inputs:
        audio_bytes 
            async api bytes of audio 
      Returns: 
        None
    '''

    leftover = b""
    async for raw in audio_bytes.iter_bytes():
        data = leftover + raw
        if len(data) % 2:
            leftover = data[-1:]
            data = data[:-1]
        else:
            leftover = b""
        resample = resample_pcm_24k_to_32k(data)
        callback(resample, 32000)



