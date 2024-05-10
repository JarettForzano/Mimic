import asyncio
import re
import time
from openai import OpenAI
import requests
import websockets
import json
import base64
from phone.completion import is_complete
from phone.prompt import prompt
import os
from dotenv import find_dotenv, load_dotenv

"""
Loads all of the environment variables

Gets messy if you try to store them outside so must be either in directory or in sub directory
"""
load_dotenv(find_dotenv('totallysecret.env'))
DEEPGRAM = os.getenv('DEEPGRAM_API_KEY')
GROQ = os.getenv('GROQ_API')
GPT = os.getenv('GPT_API_KEY')


"""
Collects each part of the user says and creates a transcript

Can also be used to time from first word caught to last
"""
class TranscriptCollector:
    def __init__(self):
        self.reset()
    def reset(self): 
        self.transcript_parts = []

    def add_part(self, part):
        self.transcript_parts.append(part)

    def get_full_transcript(self):
        return ' '.join(self.transcript_parts) # Constructs final sentence 

transcript_collector = TranscriptCollector()
response_chunks = []

# Connects to the deepgram websocket to send the text through and recieve the audio
def deepgram_connect():
    extra_headers = {'Authorization': 'Token ' + DEEPGRAM}
    deepgram_ws = websockets.connect("wss://api.deepgram.com/v1/listen?encoding=mulaw&sample_rate=8000&endpointing=true", extra_headers = extra_headers)
    
    return deepgram_ws

"""
Asynchronously creates chunks and pushes them to the stack at the same time that twilio sender is being run

As the answer is being generated the chunks are created and sent to deepgram to convert into audio which also is chunked
"""
async def prompt(text, api_Key):
    global response_chunks
    client = OpenAI(api_key=api_Key)
    #print("INPUT: " + text)
    result = client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = True
    )

    clause = ""
    count = 0
    start = time.time()
    for chunk in result:
        #print(chunk.choices[0].delta.content)
        if chunk.choices[0].delta.content is not None:
            chunk_text = chunk.choices[0].delta.content
            clause += chunk_text
            count+=1
            if contains_clause_boundary(clause) and len(clause.split()) > 3:
                response_chunks.append(clause)
                #print(clause)
                print(clause + ": [" + str(time.time()-start) + "] GPT")
                clause = ""
                count = 0
                start = time.time()


def contains_clause_boundary(text):
    pattern = re.compile(CLAUSE_BOUNDARIES)
    return bool(pattern.search(text))

CLAUSE_BOUNDARIES = r'\.|\?|!|;|,(\s*(and|but|or|nor|for|yet|so))?'


"""
This takes the twilio websocket, the streamid which is stored inside of the websocket and the text we wish to transmit over the websocket

Audio needs to be encoded with mulaw in order to work and the phone sample rate is always 8000
This can be kept inside of the proxy but in order to decrease complexity it is moved out
"""
async def twilio_sender(twilio_ws, streamsid):
        global response_chunks
        print('twilio_sender started')
        # make a Deepgram Aura TTS request specifying that we want raw mulaw audio as the output
        url = 'https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none'
        headers = {
            'Authorization': 'Token ' + DEEPGRAM,
            'Content-Type': 'application/json'
        }

        while not response_chunks: # if nothing is inside the stack we must wait
            await asyncio.sleep(0.05)

        for chunk in response_chunks:
            #print(chunk)
            payload = {
                'text': chunk
            }
            start = time.time()
            tts_response = requests.post(url, headers=headers, json=payload, stream=True)  # Stream the response
            print(chunk + ": [" + str(time.time() - start) + "] TWILIO")
            # print(tts_response)
            if tts_response.status_code == 200:
                # Stream the content directly into raw_mulaw
                for raw_mulaw in tts_response.iter_content(chunk_size=1024):
                    media_message = {
                        'event': 'media',
                        'streamSid': streamsid,
                        'media': {
                            'payload': base64.b64encode(raw_mulaw).decode('ascii')
                        }
                    }

                    # send the TTS audio to the attached phonecall
                    await twilio_ws.send(json.dumps(media_message))
        response_chunks = []



"""
This is the proxy that the twilio websocket connects to

The deepgram websocket gets connected and starts listening for audio and sends to deepgram services for a transcription
Deepgram reciever takes in the deepgram websocket and the twilio websocket, deepgram socket retrieves the json response with the transcript attatched
Twilio websocket is used transmit the response from gpt once recieved
"""

async def proxy(client_ws):
    outbox = asyncio.Queue()
    print('started proxy')
    stream_sid = None

    # Connects to the deepgram websocket
    async with deepgram_connect() as deepgram_ws:
        async def deepgram_sender(deepgram_ws):
            print('started deepgram sender')
            while True:
                chunk = await outbox.get()
                await deepgram_ws.send(chunk)

        # passes in deepgram websocket and twilio websocket to transmit and recieve data async
        async def deepgram_receiver(deepgram_ws, client_ws):
            print('started deepgram receiver')
            nonlocal stream_sid
            async for message in deepgram_ws:
                try:
                    dg_json = json.loads(message)
                    sentence = dg_json["channel"]["alternatives"][0]["transcript"] # Whatever deepgram picked up from the call

                    try:
                        if not dg_json["is_final"]: # if not final adds the part to the sentence
                            transcript_collector.add_part(sentence)
                        else:
                            transcript_collector.add_part(sentence) # adds the final piece to the sentence
                            full_sentence = transcript_collector.get_full_transcript()
                            if(is_complete(GROQ, full_sentence.strip()) == "yes"): # asks groq hey is this a good enough sentence to ask gpt
                                transcript_collector.reset()
                                await asyncio.gather(twilio_sender(client_ws, stream_sid), prompt(full_sentence.strip(), GPT))

                    except:
                        print('did not receive a standard streaming result')
                        continue
                except:
                    print('was not able to parse deepgram response as json')
                    continue
            print('finished deepgram receiver')
            transcript_collector.reset() # if call suddenly cuts out we need to reset the transcript stored

        async def client_receiver(client_ws):
            print('started client receiver')
            nonlocal stream_sid
            # we will use a buffer of 20 messages (20 * 160 bytes, 0.4 seconds) to improve throughput performance
            BUFFER_SIZE = 20 * 160
            buffer = bytearray(b'')
            empty_byte_received = False

            async for message in client_ws:
                try:
                    data = json.loads(message)

                    if data["event"] == "start":
                        print("Media WS: Received event connected or start")
                        stream_sid = data['start']['streamSid'] # needed to send audio through the websocket
                        continue
                    if data["event"] == "media":
                        media = data["media"]
                        chunk = base64.b64decode(media["payload"])
                        buffer.extend(chunk)
                        if chunk == b'':
                            empty_byte_received = True
                    if data["event"] == "stop":
                        print("Media WS: Received event stop")
                        break

                    # check if our buffer is ready to send to our outbox (and, thus, then to deepgram)
                    if len(buffer) >= BUFFER_SIZE or empty_byte_received:
                        outbox.put_nowait(buffer)
                        buffer = bytearray(b'')
                except:
                    print('message from client not formatted correctly, bailing')
                    break

            # if the empty byte was received, the async for loop should end, and we should here forward the empty byte to deepgram
            # or, if the empty byte was not received, but the WS connection to the client (twilio) died, then the async for loop will end and we should forward an empty byte to deepgram
            outbox.put_nowait(b'')
            print('finished client receiver')

        await asyncio.wait([
            asyncio.ensure_future(deepgram_sender(deepgram_ws)),
            asyncio.ensure_future(deepgram_receiver(deepgram_ws, client_ws)),
            asyncio.ensure_future(client_receiver(client_ws))
        ])

        client_ws.close()
        print('finished running the proxy')