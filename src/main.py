import asyncio
from data.information import ENV
from voice.record import voice_to_text
from gpt4.prompt import prompt
if __name__ == "__main__":

    # Inits the env varibales to be used in order to access api keys
    ENV()
    
    # Api information will be accessed here
    deepgram_api_key = ENV.retrieve("DEEPGRAM_API_KEY")
    groq_api_Key = ENV.retrieve("GROG_API")
    gpt_api_key =  ENV.retrieve("GPT_API_KEY")

    # Starts recording the users voice and returns the queries (will probably thread it at some point when the other api's are created)
    #asyncio.run(voice_to_text(deepgram_api_key, groq_api_Key))
    #print(gpt_api_key)
    prompt("Who is the 22nd president of the united states?", gpt_api_key)