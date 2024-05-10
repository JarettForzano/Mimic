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
        stream=False,
    )
    result = chat_completion.choices[0].message.content.lower() # Extract response from json
    #print(result, sentence)
    end = time.time()
    #print("Time to return groq response: " + str(end-start))
    return result