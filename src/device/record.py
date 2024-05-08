from completion import is_complete
import asyncio
import time

from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
    DeepgramClientOptions,
)

# Handles constructing the sentence for groq analysis
class TranscriptCollector:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.reset()

    def reset(self): # Also starts the timer for the voice to text
        self.transcript_parts = []
        self.start_time = None
        self.end_time = None

    def add_part(self, part):
        if not self.start_time:  
            self.start_time = time.time()
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        self.end_time = time.time()
        return ' '.join(self.transcript_parts) # Constructs final sentence 

transcript_collector = TranscriptCollector()

async def voice_to_text(api_key, groq_api):
    try:
        config = DeepgramClientOptions(options={"keepalive": "true"}) # keeps the socket alive even if nothing is being transmitted
        deepgram: DeepgramClient = DeepgramClient(api_key, config)
        dg_connection = deepgram.listen.asynclive.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript

            # print (sentence) # Debugging purposes
            
            if not result.speech_final:
                transcript_collector.add_part(sentence)
            else:
                transcript_collector.add_part(sentence)
                full_sentence = transcript_collector.get_full_transcript()
                if(is_complete(groq_api, full_sentence) == "yes"):
                    duration = transcript_collector.end_time - transcript_collector.start_time

                    print(f"speaker: [{duration}] {full_sentence}")
                    transcript_collector.reset()



        async def on_error(self, error, **kwargs):
            print(f"Handled Error: {error}")

        async def on_unhandled(self, unhandled, **kwargs):
            print(f"Unhandled Websocket Message: {unhandled}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)


        options = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            smart_format=True,
            channels=1,
            sample_rate=16000,
            endpointing=True
        )

        addons = {
            "no_delay": "true"
        }

        await dg_connection.start(options, addons=addons)

        microphone = Microphone(dg_connection.send)

        microphone.start()

        while True:
            if not microphone.is_active():
                break
            await asyncio.sleep(1)

        microphone.finish()

        dg_connection.finish()

        print("Finished")

    except Exception as e:
        print(f"Could not open socket: {e}")
        return