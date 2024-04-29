from openai import OpenAI

# inits the gpt4 client with the api key
def init(env):
    api_key = env.retrieve("GPT4_API_KEY")
    client = OpenAI(api_key)

    return client




