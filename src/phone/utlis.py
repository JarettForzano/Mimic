import json

async def hang_up(streamsid, websocket):
    message = {
        "action": "hangup",
        "call_sid": streamsid
    }
    await websocket.send(json.dumps(message))

def extract_name(response, client):
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": "Parse the name, date, time from the following response. Format like so name, date, time"
            },
            {
                "role": "user",
                "content": response
            }
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return completion.choices[0].message.split(',')

TWILIO_NUMBER, MY_NUMBER = '' # This is just till i decide to put it into the main system

def send_text(client, text):
    message = client.messages.create(
        body=text,
        from_=TWILIO_NUMBER,
        to=MY_NUMBER
    )

    message.body