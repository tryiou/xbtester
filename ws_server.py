import asyncio
import pickle
import time
from datetime import datetime
import ccxt
import websockets

# CACHE ORDERBOOK/BALANCES DATA FROM CCXT TO BE USED BY MULTIPLE BOTS

# SERVER SIDE
port = 6666
update_delay = 2.5  # DELAY BEFORE REFRESH DATA, ELSE SEND CACHED


class Pair:
    def __init__(self, symbol):
        self.symbol = symbol
        separator = self.symbol.find("/")
        self.coin1 = self.symbol[0:separator]
        self.coin2 = self.symbol[separator + 1:]
        self.orderbook = None
        self.orderbook_timer = None


def init_ccxt_instance(exchange, hostname=None):
    if exchange in ccxt.exchanges:
        exchange_class = getattr(ccxt, exchange)
        if hostname:
            instance = exchange_class({
                # 'apiKey': api,
                # 'secret': api_secret,
                'enableRateLimit': True,
                'rateLimit': 1000,
                'hostname': hostname,  # 'global.bittrex.com',
            })
        else:
            instance = exchange_class({
                # 'apiKey': api,
                # 'secret': api_secret,
                'enableRateLimit': True,
                'rateLimit': 1000,
            })
        err_count = 0
        while True:
            try:
                instance.load_markets()
            except Exception as e:
                err_count += 1
                ccxt_manage_error(e, err_count)
                time.sleep(err_count)
            else:
                break
        return instance


def ccxt_manage_error(error, err_count=1):
    print(type(error), error)
    err_type = type(error).__name__
    if (err_type == "NetworkError" or
            err_type == "DDoSProtection" or
            err_type == "RateLimitExceeded" or
            err_type == "InvalidNonce" or
            err_type == "RequestTimeout" or
            err_type == "ExchangeNotAvailable" or
            err_type == "Errno -3" or
            err_type == "AuthenticationError" or
            err_type == "Temporary failure in name resolution" or
            err_type == "ExchangeError" or
            err_type == "BadResponse"):
        time.sleep(err_count * 2)
    else:
        exit()


def ccxt_call_fetch_order_book(symbol, ccxt_o, limit=25):
    timer_perf = time.time()
    err_count = 0
    while True:
        try:
            result = ccxt_o.fetch_order_book(symbol, limit)
        except Exception as error:
            err_count += 1
            ccxt_manage_error(error, err_count)
        else:
            return result


def check_pair(message):
    separator = message.find('(')
    symbol = message[separator + 1:-1]
    if len(symbol) < 7:
        print("error with message", message, "symbol", symbol)
        return None
    pair = next((x for x in my_pairs_list if x.symbol == symbol), None)
    if not pair:
        my_pairs_list.append(Pair(symbol))
        return my_pairs_list[-1]
    else:
        return pair


def ws_get_ob(message):
    # get orderbook from ccxt, buffer with update_delay
    global ccxt_call_count, total_call_count
    total_call_count += 1
    pair_o = check_pair(message)
    if pair_o and (pair_o.orderbook_timer is None or time.time() - pair_o.orderbook_timer > update_delay):
        pair_o.orderbook = ccxt_call_fetch_order_book(pair_o.symbol, ccxt_cex)
        ccxt_call_count += 1
        pair_o.orderbook_timer = time.time()
    return pair_o.orderbook


def check_message(message):
    if len(message) >= 8:
        separator = message.find('(')
        if separator != -1:
            return True
    return False


async def echo(ws, path):
    # print("A client just connected")
    connected.add(ws)
    try:
        async for message in ws:
            if total_call_count > 0 and ccxt_call_count > 0:
                ratio = ccxt_call_count / total_call_count
            else:
                ratio = 1
            print(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), message, "ccxt", ccxt_call_count, "total",
                  total_call_count, "ratio", ratio)
            if check_message(message):
                if "get_ob(" == message[0:7]:
                    res = ws_get_ob(message)
                    await ws.send(pickle.dumps(res))
                else:
                    await ws.send(pickle.dumps("Unknown message"))
            else:
                await ws.send(pickle.dumps("Unknown message"))
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
        print(e)
    finally:
        # print("A client just disconnected")
        connected.remove(ws)



if __name__ == '__main__':
    print("WS Server listening on Port", port)
    ccxt_cex = init_ccxt_instance("bittrex", "global.bittrex.com")
    total_timer = time.time()
    ccxt_call_count = 0
    total_call_count = 0
    bal_timer = None
    bal = None
    my_pairs_list = []
    connected = set()
    start_server = websockets.serve(echo, "localhost", port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
