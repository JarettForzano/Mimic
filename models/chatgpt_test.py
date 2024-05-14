import time
from openai import AsyncOpenAI
import asyncio

client = AsyncOpenAI(api_key='')
start = None
async def gpt_stream(text):
    global start
    result = await client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = True,
    temperature=1
    )

    async for chunk in result:
        chunk_text = chunk.choices[0].delta.content
        #print( chunk_text)
        print(str(time.time()-start))
    

async def main():
    global start
    start = time.time()
    await gpt_stream("What is the most popular place in new york city") 

if __name__ == "__main__":
    asyncio.run(main())