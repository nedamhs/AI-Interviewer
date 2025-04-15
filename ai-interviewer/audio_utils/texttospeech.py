import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
openai = AsyncOpenAI(api_key=os.environ.get("OPENAI-API-KEY"))


async def text_to_audio(text: str):
  '''Creates a stream of  audio'''
  async with openai.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input=text,
    response_format="pcm",
  ) as response:
    await set_virtual_mic(response)


async def set_virtual_mic(audio_bytes: bytes):
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
    
