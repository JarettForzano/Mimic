import json

async def hang_up(streamsid, websocket):
    message = {
        "action": "hangup",
        "call_sid": streamsid
    }
    await websocket.send(json.dumps(message))


def add_dates():
    return