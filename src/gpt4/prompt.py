from openai import OpenAI

def prompt(text, api_Key):
    client = OpenAI(api_key=api_Key)

    result = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide short answers to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = True
    )

    for chunk in result:
        print(
            chunk.choices[0].delta.get("content", ""),
            end = "",
            flush=True
        )