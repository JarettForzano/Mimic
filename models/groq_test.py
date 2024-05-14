import asyncio
import time
from groq import AsyncGroq

client = AsyncGroq(api_key='')
start = time.time()

history = [{
            "role": "system",
            "content": """The user is calling to schedule an appointment with a person named Jarett. You are his assistant, make sure to follow the steps assigned and confirm information at the end.
                1. Confirm they are calling to make an appointment
                2. Confirm the users name
                3. Get when they are next available
                4. Schedule an appointment with the given date and time
                5. Tell them at the end that Jarett will call at exactly the time designated.
                6. Do not include any more information than needed and do not go outside the domain of an assistant for Jarett.
                7. If user provides details before you request them, you can skip that part
                """
            },]

async def groq_stream(text):
    global start
    global history
    history.append({ "role": "user", "content": text,}) # appends question to history

    stream = await client.chat.completions.create(
        messages = history,
        model="llama3-8b-8192",
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )
    response = ""
    async for chunk in stream:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:
            response += chunk_text
        #print(chunk_text)
        ##print(str(time.time()-start))
    history.append({ "role": "system", "content": response,})
    print(response)

async def main():
    global start
    global history  # Access the global message history variable
    start = time.time()
    await groq_stream("Hello")
    #await groq_stream("What was my previous question?") 
    #print(history)


if __name__ == "__main__":
    asyncio.run(main())
