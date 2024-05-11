import asyncio
import time
from openai import OpenAI
import re

response_chunks = []
## Just used to test it out
"""
Asynchronously creates chunks and pushes them to the stack at the same time that twilio sender is being run

As the answer is being generated the chunks are created and sent to deepgram to convert into audio which also is chunked
"""
async def prompt(text, api_Key):
    global response_chunks
    client = OpenAI(api_key=api_Key)

    result = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = True
    )

    clause = ""
    count = 0
    start = time.time()
    for chunk in result:
        #print(chunk.choices[0].delta.content)
        if chunk.choices[0].delta.content is not None:
            chunk_text = chunk.choices[0].delta.content
            clause += chunk_text
            count+=1
            if contains_clause_boundary(clause) and len(clause.split()) > 3:
                response_chunks.append(clause)
                #print(clause)
                print(clause + ": [" + str(time.time()-start) + "] GPT")
                clause = ""
                count = 0
                start = time.time()


def contains_clause_boundary(text):
    pattern = re.compile(CLAUSE_BOUNDARIES)
    return bool(pattern.search(text))

CLAUSE_BOUNDARIES = r'\.|\?|!|;|,(\s*(and|but|or|nor|for|yet|so))?'