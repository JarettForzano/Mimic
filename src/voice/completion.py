from groq import Groq

# Using groq, provides a yes or no response as to if the sentence is complete or not
def is_complete(api_key, sentence):
    if sentence is None or sentence == "":
        return "no"
    # Takes the api key
    client = Groq(api_key=api_key)
    #print("Sentence: " + sentence)
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


        model="llama3-70b-8192",

        temperature=0.0,
        max_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    # Debugging purposes
    return chat_completion.choices[0].message.content.lower()


