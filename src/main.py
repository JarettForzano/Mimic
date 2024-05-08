import asyncio
import sys
import websockets
from phone.server import *


# Currently runs the phone feature
def main():
	proxy_server = websockets.serve(proxy, 'localhost', 5000)

	asyncio.get_event_loop().run_until_complete(proxy_server)
	asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
	sys.exit(main() or 0)