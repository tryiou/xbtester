import json
import os
import time
import ccxt
from logger import *

ccxt_log = setup_logger(name="CCXT_LOG", log_file='logs/ccxt.log', level=logging.INFO)


def init_ccxt_instance(exchange, hostname=None):
    # CCXT instance
    # script_dir = os.path.dirname(__file__)
    # with open(script_dir + '/utils/keys.local.json') as json_file:
    #     data_json = json.load(json_file)
    #     api = None
    #     api_secret = None
    #     for data in data_json['api_info']:
    #         if exchange in data['exchange']:
    #             api = data['api']
    #             api_secret = data['secret']
    #             break
    #     if not (api and api_secret):
    #         print(exchange, "need api key set in /utils/keys.local.json")
    #         exit()
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
