import asyncio
import time
from openai import OpenAI
import re

stack = []

# gpt prompt response to what the user asks, made to be kept short to lower token intake
async def prompt(text, api_Key):
    start = time.time()
    client = OpenAI(api_key=api_Key)
    #print("INPUT: " + text)
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
    for chunk in result:
        #print(chunk.choices[0].delta.content)
        if chunk.choices[0].delta.content is not None:
            chunk_text = chunk.choices[0].delta.content
            clause += chunk_text
            count+=1
            if contains_clause_boundary(chunk_text) or count == 5:
                stack.append(clause)
                print(clause)
                clause = ""
                count = 0
            #end = time.time()
            #print("Time for gpt response: " + str(end-start))


def contains_clause_boundary(text):
    pattern = re.compile(CLAUSE_BOUNDARIES)
    return bool(pattern.search(text))

CLAUSE_BOUNDARIES = r'\.|\?|!|;|,(\s*(and|but|or|nor|for|yet|so))?'

