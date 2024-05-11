from openai import AsyncOpenAI

client = AsyncOpenAI(api_key='')

async def gpt_stream(text, ws, stream_sid):
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

    async def text_iterator():
        async for chunk in result:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
    await text_to_speech_input_streaming(text_iterator(), ws, stream_sid)


async def text_to_speech_input_streaming(text_iterator, ws, stream_sid):
    return