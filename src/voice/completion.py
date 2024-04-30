from groq import Groq

# Using groq, provides a yes or no response as to if the sentence is complete or not
def is_complete(api_key, sentence):

    # Takes the api key
    client = Groq(api_key)

    chat_completion = client.chat.completions.create(

        messages=[
            {
                "role": "system",
                "content": "You are only allowed to respond with yes or no when answering if the following sentence is a complete sentence or not"
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
    # print(chat_completion.choices[0].message.content)

    return chat_completion.choices[0].message.content