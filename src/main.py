from data.information import ENV
from voice.record import record_audio

if __name__ == "__main__":

    # Inits the env varibales to be used in order to access api keys
    ENV()
    
    # Api information will be accessed here
    deepgram_api_key = ENV.retrieve("DEEPGRAM_API_KEY")

    # Starts recording the users voice and returns the queries (will probably thread it at some point when the other api's are created)
    record_audio(deepgram_api_key)