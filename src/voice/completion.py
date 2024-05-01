from groq import Groq

# Using groq, provides a yes or no response as to if the sentence is complete or not
def is_complete(api_key, sentence):

    # okay sooooo yeah this makes it work 100% of the time. Its my counter to long pauses but i dont think this would actually occur in real convo's so its more of an edge case cover
    if sentence is None or sentence == "":
        return "no"
    
    # Takes the api key
    client = Groq(api_key=api_key)
    
    #print("Sentence: " + sentence) # use to debug
    chat_completion = client.chat.completions.create(

        messages=[
            {
                "role": "system",
                "content": "The content should simply be Yes or No depending on whether the following sentence is considered complete or not. Questions are considered complete sentences."
            },

            {
                "role": "user",
                "content": sentence,
            }
        ],


        model="llama3-70b-8192", # Fast model :)

        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return chat_completion.choices[0].message.content.lower() # returns response 


