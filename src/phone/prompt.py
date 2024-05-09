from openai import OpenAI

# gpt prompt response to what the user asks, made to be kept short to lower token intake
def prompt(text, api_Key):
    client = OpenAI(api_key=api_Key)

    result = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide short answers to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = False # CANNOT STREAM
    )

    result = result['choices'][0]['message']['content'] # Extract response from the json

    return result