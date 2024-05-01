import asyncio
from data.information import ENV
from voice.record import voice_to_text
if __name__ == "__main__":

    # Inits the env varibales to be used in order to access api keys
    ENV()
    
    # Api information will be accessed here
    deepgram_api_key = ENV.retrieve("DEEPGRAM_API_KEY")
    api_Key = ENV.retrieve("GROG_API")

    # Starts recording the users voice and returns the queries (will probably thread it at some point when the other api's are created)
    asyncio.run(voice_to_text(deepgram_api_key, api_Key))