from groq import Groq

# Using groq, provides a yes or no response as to if the sentence is complete or not
def is_complete(api_key, sentence):
    if sentence is None or sentence == "": # just return if nothing is present
        return "no"
    
    # Takes the api key
    client = Groq(api_key=api_key)
    
    #print("Sentence recieved: " + sentence) # use to debug
    chat_completion = client.chat.completions.create(

        messages=[
            {
                "role": "system",
                "content": "The content should simply be Yes or No depending on if the string of words is a full sentence or a question fragment. Context is not needed."
            },

            {
                "role": "user",
                "content": sentence,
            }
        ],


        model="llama3-70b-8192", # Fast model

        temperature=1, # do not change, if it goes lower then the result becomes inaccurate
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    result = chat_completion.choices[0].message.content.lower()
    #print(result)
    return result


