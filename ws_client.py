import asyncio
import pickle
import websockets
import datetime
import time


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


# CLIENT SIDE

async def ws_get_ob(symbol):
    url = "ws://127.0.0.1:6666"
    async with websockets.connect(url) as ws:
        await ws.send('get_ob(' + symbol + ')')
        msg = pickle.loads(await ws.recv())
        if __name__ == '__main__':
            print(msg)
        return msg


# TEST
if __name__ == '__main__':
    while 1:
        print(datetime.datetime.now())
        asyncio.get_event_loop().run_until_complete(ws_get_ob("BLOCK/BTC"))
        asyncio.get_event_loop().run_until_complete(ws_get_ob("LTC/BTC"))
        time.sleep(0.2)
