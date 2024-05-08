import asyncio
import sys
import requests
import websockets
import json
import base64
import time
from phone.completion import is_complete
from phone.prompt import prompt
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv('totallysecret.env'))
DEEPGRAM = os.getenv('DEEPGRAM_API_KEY')
GROQ = os.getenv('GROQ_API')
GPT = os.getenv('GPT_API_KEY')

print(DEEPGRAM, GROQ, GPT)
class TranscriptCollector:
	def __init__(self):
		self.reset()
	def reset(self): # Also starts the timer for the voice to text
		self.transcript_parts = []

	def add_part(self, part):
		self.transcript_parts.append(part)

	def get_full_transcript(self):
		return ' '.join(self.transcript_parts) # Constructs final sentence 

transcript_collector = TranscriptCollector()

def deepgram_connect():
   	# Replace with your Deepgram API key.
	extra_headers = {'Authorization': 'Token {DEEPGRAM}'}
	deepgram_ws = websockets.connect("wss://api.deepgram.com/v1/listen?encoding=mulaw&sample_rate=8000&endpointing=true", extra_headers = extra_headers)
	
	return deepgram_ws

def twilio_sender(twilio_ws, data, text):
        print('twilio_sender started')

        # wait to receive the streamsid for this connection from one of Twilio's messages
        streamsid = data['start']['streamSid']

        # make a Deepgram Aura TTS request specifying that we want raw mulaw audio as the output
        url = 'https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none'
        headers = {
            'Authorization': 'Token {DEEPGRAM}',
            'Content-Type': 'application/json'
        }
        payload = {
            'text': text
        }
        tts_response = requests.post(url, headers=headers, json=payload)

        if tts_response.status_code == 200:
            raw_mulaw = tts_response.content

            # construct a Twilio media message with the raw mulaw (see https://www.twilio.com/docs/voice/twiml/stream#websocket-messages---to-twilio)
            media_message = {
                'event': 'media',
                'streamSid': streamsid,
                'media': {
                    'payload': base64.b64encode(raw_mulaw).decode('ascii')
                }
            }

            # send the TTS audio to the attached phonecall
            twilio_ws.send(json.dumps(media_message))

async def proxy(client_ws):
	outbox = asyncio.Queue()
	print('started proxy')

	
	async with deepgram_connect() as deepgram_ws:
		async def deepgram_sender(deepgram_ws):
			print('started deepgram sender')
			while True:
				chunk = await outbox.get()
				await deepgram_ws.send(chunk)

		async def deepgram_receiver(deepgram_ws, client_ws):
			print('started deepgram receiver')
			async for message in deepgram_ws:
				try:
					dg_json = json.loads(message)

					# print the results from deepgram!
					sentence = dg_json["channel"]["alternatives"][0]["transcript"]

					try:
						if not dg_json["is_final"]:
							transcript_collector.add_part(sentence)
							print("Added part: " + sentence)
						else:
							start_time = time.time()
							transcript_collector.add_part(sentence)
							full_sentence = transcript_collector.get_full_transcript()
							print("full sentence: " + full_sentence)
							if(is_complete(GROQ, full_sentence.strip()) == "yes"):
								end_time = time.time()
								duration = end_time - start_time
								print(f"speaker: [{duration}] {full_sentence}")
								transcript_collector.reset()
								async for message in client_ws:
									try:
										data = json.loads(message)
										response = prompt(full_sentence.strip(), GPT)
										await twilio_sender(client_ws, data, response)
									except:
										break


					except:
						print('did not receive a standard streaming result')
						continue
				except:
					print('was not able to parse deepgram response as json')
					continue
			print('finished deepgram receiver')
			transcript_collector.reset()

		async def client_receiver(client_ws):
			print('started client receiver')

			# we will use a buffer of 20 messages (20 * 160 bytes, 0.4 seconds) to improve throughput performance
			# NOTE: twilio seems to consistently send media messages of 160 bytes
			BUFFER_SIZE = 20 * 160
			buffer = bytearray(b'')
			empty_byte_received = False
			async for message in client_ws:
				try:
					data = json.loads(message)
					if data["event"] in ("connected", "start"):
						print("Media WS: Received event connected or start")
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