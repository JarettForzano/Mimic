import time
from openai import OpenAI
import re

# gpt prompt response to what the user asks, made to be kept short to lower token intake
def prompt(text, api_Key):
    start = time.time()
    client = OpenAI(api_key=api_Key)
    #print("INPUT: " + text)
    result = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = False # CANNOT STREAM
    )

    answer = result.choices[0].message.content # Extract response from the json
    end = time.time()
    #print("Time for gpt response: " + str(end-start))
    return chunk_text_dynamically(answer)

CLAUSE_BOUNDARIES = r'\.|\?|!|;|, (and|but|or|nor|for|yet|so)'
MAX_CHUNK_LENGTH = 40

def chunk_text_dynamically(text):
    # Find clause boundaries using regular expression
    clause_boundaries = re.finditer(CLAUSE_BOUNDARIES, text)
    boundaries_indices = [boundary.start() for boundary in clause_boundaries]

    chunks = []
    start = 0
    # Add chunks until the last clause boundary
    for boundary_index in boundaries_indices:
        chunk = text[start:boundary_index + 1].strip()
        if len(chunk) <= MAX_CHUNK_LENGTH:
            chunks.append(chunk)
        else:
            # Split by comma if it doesn't create subchunks less than three words
            subchunks = chunk.split(',')
            temp_chunk = ''
            for subchunk in subchunks:
                if len(temp_chunk) + len(subchunk) <= MAX_CHUNK_LENGTH:
                    temp_chunk += subchunk + ','
                else:
                    if len(temp_chunk.split()) >= 3:
                        chunks.append(temp_chunk.strip())
                    temp_chunk = subchunk + ','
            if temp_chunk:
                if len(temp_chunk.split()) >= 3:
                    chunks.append(temp_chunk.strip())
        start = boundary_index + 1

    # Split remaining text into subchunks if needed
    remaining_text = text[start:].strip()
    if remaining_text:
        remaining_subchunks = [remaining_text[i:i+MAX_CHUNK_LENGTH] for i in range(0, len(remaining_text), MAX_CHUNK_LENGTH)]
        chunks.extend(remaining_subchunks)

    return chunks