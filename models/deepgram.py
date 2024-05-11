import asyncio
import base64
import json
import requests

response_queue = asyncio.Queue()
DEEPGRAM = ''

async def twilio_sender(twilio_ws, streamsid):
        global response_chunks
        print('twilio_sender started')
        # make a Deepgram Aura TTS request specifying that we want raw mulaw audio as the output
        url = 'https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none'
        headers = {
            'Authorization': 'Token ' + DEEPGRAM,
            'Content-Type': 'application/json'
        }

        while True:
            chunk = await response_queue.get()
            chunk_text = chunk.strip()
            if(chunk_text == "close"):
                break;
            payload = {
                'text': chunk_text
            }
            #start = time.time()
            tts_response = requests.post(url, headers=headers, json=payload, stream=True)  # Stream the response
            #print(chunk_text + ": [" + str(time.time() - start) + "] DEEPGRAM")
            # print(tts_response)
            if tts_response.status_code == 200:
                # Stream the content directly into raw_mulaw
                for raw_mulaw in tts_response.iter_content(chunk_size=256):
                    media_message = {
                        'event': 'media',
                        'streamSid': streamsid,
                        'media': {
                                'payload': base64.b64encode(raw_mulaw).decode('ascii')
                        }
                    }

                    # send the TTS audio to the attached phonecall
                    await twilio_ws.send(json.dumps(media_message))