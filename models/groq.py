from groq import AsyncGroq

client = AsyncGroq()

async def groq_stream(text, ws, stream_sid):
    stream = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."
            },
            {
                "role": "user",
                "content": text,
            }
        ],

        model="llama3-8b-8192",
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )

    async def text_iterator():
        async for chunk in stream:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
    await text_to_speech_input_streaming(text_iterator(), ws, stream_sid)

async def text_to_speech_input_streaming(text_iterator, ws, stream_sid):
    return