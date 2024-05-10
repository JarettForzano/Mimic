import time
from groq import Groq

"""
Groq is used to make the audio to text portion more efficent

By testing if the sentence is complete or not we can avoid false pushes to gpt and make the answers more specific
"""
def is_complete(api_key, sentence):
    if sentence is None or sentence == "": # just return if nothing is present
        return "no"
    start = time.time()
    print("Pushed: " + sentence)
    # Takes the api key
    client = Groq(api_key=api_key)
    
    chat_completion = client.chat.completions.create(

        messages=[
            {
                "role": "system",
                "content": "Yes or no, is this a sentence or a question?. Context is not needed."
            },
            {
                "role": "user",
                "content": sentence,
            }
        ],


        model="llama3-8b-8192", # Fast model

        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=True,
    )
    for chunk in chat_completion:
        chunk_text = chunk.choices[0].delta.content.lower()
        if chunk_text == "yes" or chunk_text == "no":
            print(chunk_text + ": [" + str(time.time()-start) + "] GROQ")
            return chunk_text