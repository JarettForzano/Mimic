import asyncio
import time
from openai import AsyncOpenAI
import websockets
import json
import base64
import os
from dotenv import find_dotenv, load_dotenv
start = None
"""
Loads all of the environment variables

Gets messy if you try to store them outside so must be either in directory or in sub directory
"""
load_dotenv(find_dotenv('totallysecret.env'))
DEEPGRAM = os.getenv('DEEPGRAM_API_KEY')
GROQ = os.getenv('GROQ_API')
GPT = os.getenv('GPT_API_KEY')
LABS = os.getenv('ELEVEN_API')
client = AsyncOpenAI(api_key=GPT)

# Connects to the deepgram websocket to send the text through and recieve the audio
def deepgram_connect():
    extra_headers = {'Authorization': 'Token ' + DEEPGRAM}
    deepgram_ws = websockets.connect("wss://api.deepgram.com/v1/listen?model=enhanced-phonecall&encoding=mulaw&smart_format=true&sample_rate=8000&endpointing=true", extra_headers = extra_headers)
    
    return deepgram_ws

async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""
    async for text in chunks:
        #print(text)
        if text:
            if buffer.endswith(splitters):
                yield buffer + " "
                buffer = text
            elif text.startswith(splitters):
                yield buffer + text[0] + " "
                buffer = text[1:]
            else:
                buffer += text

    if buffer:
        yield buffer + " "

"""
Asynchronously creates chunks and pushes them to the stack at the same time that twilio sender is being run

As the answer is being generated the chunks are created and sent to deepgram to convert into audio which also is chunked
"""
async def gpt_stream(text, ws, stream_sid):
    global start
    result = await client.chat.completions.create(
    model = "gpt-3.5-turbo",
    messages = [
        {"role": "system", "content": "You are an assistant whose task is to communicate and provide one sentence responses to questions that the user might have."},
        {"role": "user", "content": text}
    ],
    stream = True,
    temperature=1
    )

    async def text_iterator():
        async for chunk in result:
            chunk_text = chunk.choices[0].delta.content
            yield chunk_text
    start = time.time()
    await text_to_speech_input_streaming(text_iterator(), ws, stream_sid)

async def text_to_speech_input_streaming(text_iterator, ws, stream_sid):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM/stream-input?model_id=eleven_turbo_v2&output_format=ulaw_8000&optimize_streaming_latency=3"

    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({
            "text": " ",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
            "xi_api_key": LABS
        }))

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield data["audio"]
                    elif data.get('isFinal'):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(twilio_sender(ws, stream_sid, listen()))

        async for text in text_chunker(text_iterator):
            #print(text)
            await websocket.send(json.dumps({"text": text, "try_trigger_generation": True}))

        await websocket.send(json.dumps({"text": ""}))

        await listen_task


"""
This takes the twilio websocket, the streamid which is stored inside of the websocket and the text we wish to transmit over the websocket

Audio needs to be encoded with mulaw in order to work and the phone sample rate is always 8000
This can be kept inside of the proxy but in order to decrease complexity it is moved out
"""
async def twilio_sender(twilio_ws, streamsid, audio_stream):
    print('twilio_sender started')
    global start
    async for chunk in audio_stream:
        #print(chunk)
        # Stream the content directly into twilio socket
        if chunk:
            try:
                media_message = {
                    'event': 'media',
                    'streamSid': streamsid,
                    'media': {
                        'payload': chunk
                    }
                }

                # send the TTS audio to the attached phonecall
                await twilio_ws.send(json.dumps(media_message))
                print("TTFAB: " + str(time.time() - start))
            except Exception as e:
                print("Error sending to Twilio: ", e)


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
                    #print(sentence, len(sentence.split()))
                    try:
                        #if(is_complete(GROQ, sentence.strip()) == "yes"): # asks groq hey is this a good enough sentence to ask gpt
                        if(len(sentence) != 0):
                            await gpt_stream(sentence.strip(), client_ws, stream_sid)

                    except Exception as e:
                        print('did not receive a standard streaming result', e)
                        continue
                except:
                    print('was not able to parse deepgram response as json')
                    continue
            print('finished deepgram receiver')

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