import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai = AsyncOpenAI(api_key=os.environ.get("OPENAI-API-KEY"))
# Needs ffmpeg installed
# 


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
    await set_virtual_mic(response)


async def set_virtual_mic(audio_bytes: bytes) -> None:
    '''
    Links the stream of bytes with the virtual mic and plays through it if it is set as the default device. 

    Inputs:
      audio_bytes: bytes 
          pcm audio bytes that will be streamed to the bot. 
    Returns: 
      None
    '''

    process = await asyncio.create_subprocess_exec(
        "ffplay",
        "-f", "s16le",       
        "-ar", "24000",
        "-nodisp",           
        "-autoexit",        
        "-loglevel", "error",
        "-", 
        stdin=asyncio.subprocess.PIPE
    )

    async for chunk in audio_bytes.iter_bytes():
        process.stdin.write(chunk)
        await process.stdin.drain()

    process.stdin.close()
    await process.wait()

if __name__ == "__main__":
   asyncio.run(text_to_audio("One last audio test to ensure that the text to speech is working properly!"))
    
