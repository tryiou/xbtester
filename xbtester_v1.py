import os

if not os.path.isdir('logs'):
    os.mkdir('logs')
import random
import time
from datetime import datetime, timedelta
# from pydub import AudioSegment
# from pydub.playback import play
import config
import ws_client
from ccxt_funcs_def import init_ccxt_instance, ccxt_call_fetch_order_book
from logger import *
import requests
import zipfile
import logging
import subprocess
import xb_func_defs as xb


class Dexinst:
    def __init__(self, side):
        self.side = side
        self.balances = -1
        self.open_orders = []
        # self.coin1_address = None
        # self.coin2_address = None
        self.coin_address_list = {}

    def get_addresses(self, c1, c2):
        if "A" in self.side:
            if c1 in config.dx_addresses_A:
                self.coin_address_list[c1] = config.dx_addresses_A[c1]
            else:
                if c1 not in self.coin_address_list:
                    self.coin_address_list[c1] = xb.getnewtokenadress("A", c1)[0]
                    dx_settings_save_new_address(c1, self.coin_address_list[c1], "A")
            if c2 in config.dx_addresses_A:
                self.coin_address_list[c2] = config.dx_addresses_A[c2]
            else:
                if c2 not in self.coin_address_list:
                    self.coin_address_list[c2] = xb.getnewtokenadress("A", c2)[0]
                    dx_settings_save_new_address(c2, self.coin_address_list[c2], "A")
        if "B" in self.side:
            if c1 in config.dx_addresses_B:
                self.coin_address_list[c1] = config.dx_addresses_B[c1]
            else:
                if c1 not in self.coin_address_list:
                    self.coin_address_list[c1] = xb.getnewtokenadress("B", c1)[0]
                    dx_settings_save_new_address(c1, self.coin_address_list[c1], "B")
            if c2 in config.dx_addresses_B:
                self.coin_address_list[c2] = config.dx_addresses_B[c2]
            else:
                if c2 not in self.coin_address_list:
                    self.coin_address_list[c2] = xb.getnewtokenadress("B", c2)[0]
                    dx_settings_save_new_address(c2, self.coin_address_list[c2], "B")


balances_logger = setup_logger(name="BALANCES_LOG", log_file='logs/balances.log', level=logging.INFO)
trade_logger = setup_logger(name="TRADES_LOG", log_file='logs/trades.log', level=logging.INFO)
blockcounts_logger = setup_logger(name='CC_BLOCKCOUNTS', log_file='logs/cc_blockcounts.log', level=logging.INFO)
logging.basicConfig(level=logging.INFO)

test_mode = config.test_mode
test_trade_to_do = config.test_trade_to_do
test_amount = config.test_amount
cc_on = config.cc_on
size_max = config.size_max
size_min = config.size_min
trade_to_do = config.trade_to_do
usd_volume_target = config.usd_volume_target
price_multi = config.price_multi
trade_delay = config.trade_delay
flush_delay = 60 * 15
time_delta = timedelta(minutes=0.125 / 2)
use_ws = ws_client.is_port_in_use(6666)
print('\nuse ws:', use_ws, ', test_mode:', test_mode, '\n')
if test_mode:
    markets = config.t_markets
else:
    markets = config.n_markets

xbridge_callcount_loop_timer = 60
ccblockcounts_logger_timer = 0
ccblockcounts_logger_loop_timer = 60 * 5
instance_A = Dexinst("A")
instance_B = Dexinst("B")
ccxt_bittrex = init_ccxt_instance("bittrex", "global.bittrex.com")
trade_counter = 0
total_trade_time = []
loop_time = 10
fail_count = 0
log_bal_timer = None
maker_amount = None
taker_amount = None
order_price = None
coin1coin2_cexprice = None
flush_timer = None
max_delay_initialized = 120
try:
    print("dxloadxbridgeconf A:", xb.dxloadxbridgeconf("A"))
    print("getnetworkinfo A:\n", xb.getnetworkinfo("A"))
    print("dxloadxbridgeconf B:", xb.dxloadxbridgeconf("B"))
    print("getnetworkinfo B:\n", xb.getnetworkinfo("A"))
except Exception as e:
    print(e)
    exit()


def dx_settings_save_new_address(coin, address, side):
    # SIDE A B
    filename = "config.py"
    with open(filename, "r") as fileread:
        file = fileread.readlines()
        if side == "A":
            if "dx_addresses_A[\'" + coin + "\']" not in file:
                index = file.index("dx_addresses_A = {}\n")
                file.insert(index + 1, 'dx_addresses_A[\'' + coin + '\'] = "' + address + '"\n')
                with open(filename, "w") as filewrite:
                    filewrite.writelines(file)
            else:
                index = file.index("dx_addresses_A[\'" + coin + "\']")
                file[index] = 'dx_addresses_A[\'' + coin + '\'] = "' + address + '"\n'
                with open(filename, "w") as filewrite:
                    filewrite.writelines(file)
        if side == "B":
            if "dx_addresses_B[\'" + coin + "\']" not in file:
                index = file.index("dx_addresses_B = {}\n")
                file.insert(index + 1, 'dx_addresses_B[\'' + coin + '\'] = "' + address + '"\n')
                with open(filename, "w") as filewrite:
                    filewrite.writelines(file)
            else:
                index = file.index("dx_addresses_B[\'" + coin + "\']")
                file[index] = 'dx_addresses_B[\'' + coin + '\'] = "' + address + '"\n'
                with open(filename, "w") as filewrite:
                    filewrite.writelines(file)


def config_save_fee_to_burn(side, value):
    filename = "config.py"
    with open(filename, "r") as fileread:
        file = fileread.readlines()
        for index, line in enumerate(file):
            if 'fee_to_burn[\'' + side + '\'] = ' in line:
                file[index] = 'fee_to_burn[\'' + side + '\'] = ' + str(value) + '\n'
                with open(filename, "w") as filewrite:
                    filewrite.writelines(file)


def update_fee_count(side, fee=0.0151176):
    new_amount = round(config.fee_to_burn[side] - fee, 8)
    if new_amount < 0:
        print("depleted config.fee_to_burn[" + side + "]")
        exit()
    else:
        config.fee_to_burn[side] = new_amount
        config_save_fee_to_burn(side, new_amount)


def cex_get_btc_rate_from_orderbook(coin):
    done = False
    rate = None
    while not done:
        if coin != "USD":
            if coin + "/BTC" in ccxt_bittrex.symbols:
                if use_ws:
                    cex_orderbook = ws_client.asyncio.get_event_loop().run_until_complete(
                        ws_client.ws_get_ob(coin + "/BTC"))
                else:
                    cex_orderbook = ccxt_call_fetch_order_book(coin + "/BTC", ccxt_bittrex)
            else:
                print(coin, "not in ccxt_bittrex.symbols")
                exit()
        else:
            if "BTC/" + coin in ccxt_bittrex.symbols:
                if use_ws:
                    cex_orderbook = ws_client.asyncio.get_event_loop().run_until_complete(
                        ws_client.ws_get_ob("BTC/" + coin))
                else:
                    cex_orderbook = ccxt_call_fetch_order_book("BTC/" + coin, ccxt_bittrex)
            else:
                print(coin, "not in ccxt_bittrex.symbols")
                exit()
        if "asks" in cex_orderbook and "bids" in cex_orderbook and len(cex_orderbook['asks']) > 0 and len(
                cex_orderbook['bids']) > 0:
            ask = cex_orderbook["asks"][0][0]
            bid = cex_orderbook["bids"][0][0]
            if ask > bid:
                rate = bid + (ask - bid) / 2
                done = True
            elif ask < bid:
                rate = ask + (bid - ask) / 2
                done = True
            elif ask == bid:
                rate = ask
                done = True
    if rate:
        coin_btc_price = float("{:.8f}".format(rate))
        return coin_btc_price
    else:
        return None


def get_pair_usd_volume(c1, c2):
    btcusd_r = cex_get_btc_rate_from_orderbook("USD")

    if c1 + "/BTC" in ccxt_bittrex.symbols:
        coin1_r = cex_get_btc_rate_from_orderbook(c1)
    else:
        coin1_r_usd = scrap_price_cmc(c1)
        coin1_r = coin1_r_usd / btcusd_r
    if c2 + "/BTC" in ccxt_bittrex.symbols:
        coin2_r = cex_get_btc_rate_from_orderbook(c2)
    else:
        coin2_r_usd = scrap_price_cmc(c2)
        coin2_r = coin2_r_usd / btcusd_r
    res = xb.dxgetorderfills("A", c1, c2, True)

    if len(res) == 0:
        res = xb.dxgetorderfills("B", c1, c2, True)

        if len(res) == 0:
            return 0, 0
    total_coin1 = 0
    total_coin2 = 0
    time_offset = timedelta(hours=0, minutes=0)
    for each in res:
        order_date = datetime.strptime(each['time'], "%Y-%m-%dT%H:%M:%S.%fZ")
        now = datetime.now() - time_offset
        if now - timedelta(hours=24) <= order_date <= now:
            # print(each)
            if each['maker'] == c1 and each['taker'] == c2:
                total_coin1 += float(each['maker_size'])
                total_coin2 += float(each['taker_size'])
            elif each['taker'] == c1 and each['maker'] == c2:
                total_coin1 += float(each['taker_size'])
                total_coin2 += float(each['maker_size'])
    # print(total_coin1, total_coin2, coin1_r, coin2_r, btcusd_r)
    # exit()
    c1_usd_v = total_coin1 * coin1_r * btcusd_r
    c2_usd_v = total_coin2 * coin2_r * btcusd_r
    return c1_usd_v, c2_usd_v


def merge_two_dicts(x, y):
    result = {key: str(float(x.get(key, 0)) + float(y.get(key, 0))) for key in set(x) | set(y)}
    return result


def update_dex_bals(display=False):
    global log_bal_timer
    log_bal_delay = 60
    instance_A.balances = xb.dxGetTokenBalances("A")
    instance_B.balances = xb.dxGetTokenBalances("B")
    total = merge_two_dicts(instance_A.balances, instance_B.balances)
    if not log_bal_timer or time.time() - log_bal_timer > log_bal_delay:
        balances_logger.info("** BALANCE UPDATE **")
        balances_logger.info(sorted(instance_A.balances.items()))
        balances_logger.info(sorted(instance_B.balances.items()))
        balances_logger.info(sorted(total.items()))
        balances_logger.info("fee_to_burn A: " + str(config.fee_to_burn['A']) + " fee_to_burn B: " + str(
            config.fee_to_burn['B']) + " total fee_to_burn:" + str(config.fee_to_burn['A'] + config.fee_to_burn['B']))
        log_bal_timer = time.time()


def wait_sequence(order_id, side, new_timer):
    if config.test_partial and config.test_mode:
        new_max_delay = 60 * 10
    else:
        new_max_delay = 60 * 2
    i_counter = 0
    cancel = False
    order_data = xb.getorderstatus(side, order_id)
    while 'code' in order_data:
        if time.time() - new_timer > new_max_delay:
            cancel = True
            break
        i_counter += 1
        time.sleep(0.5)
        order_data = xb.getorderstatus(side, order_id)
        if i_counter % 10 == 0:
            print("order_data_" + side + ":\n", order_data)
    i_counter = 0
    timer_print = 0
    while not cancel and "open" not in order_data['status']:
        if time.time() - new_timer > new_max_delay:
            cancel = True
            break
        i_counter += 1
        time.sleep(0.5)
        order_data = xb.getorderstatus(side, order_id)
        if timer_print == 0 or time.time() - timer_print > 10:
            print("order_data_" + side + ": " + order_data['status'])
            timer_print = time.time()
    return cancel


def wait_created_order(order_id, side=None):
    # side = A or B
    new_timer = time.time()
    cancel_a = False
    cancel_b = False
    if side == "A":
        cancel_a = wait_sequence(order_id, "A", new_timer)
        if not cancel_a:
            cancel_b = wait_sequence(order_id, "B", new_timer)
    elif side == "B":
        cancel_b = wait_sequence(order_id, "B", new_timer)
        if not cancel_b:
            cancel_a = wait_sequence(order_id, "A", new_timer)
    if cancel_a or cancel_b:
        print(xb.cancelorder(side, order_id))
        msg = "stuck on 'new', " + side + ".cancelling: " + order_id
        # print(msg)
        trade_logger.critical(msg)
        return False
    else:
        return True


def check_status_fail(status):
    failed_list = ["expired", "offline", "canceled", "invalid", "rolled back", "rollback failed"]
    for each in failed_list:
        if status == each:
            return True
    return False


def cancel_all_open_orders():
    res_a = xb.getopenorders("A")

    for order in res_a:
        msg = "A.CANCELLING:\n", order["id"]
        # print(msg)
        trade_logger.info(msg)
        # print(x)
        xb.cancelorder("A", order['id'])
        time.sleep(1)
    res_b = xb.getopenorders("B")
    for order in res_b:
        msg = "B.CANCELLING:\n", order["id"]
        # print(msg)
        trade_logger.info(msg)
        xb.cancelorder("B", order['id'])

        time.sleep(1)


def check_side_bal(side, coin1, coin2):
    maker_a = float(maker_amount)
    taker_a = float(taker_amount)
    # print("check_side_bal:", side)
    if side == "side1":
        if config.fee_to_burn['B'] < 0.0151:
            print("out of fee_to_burn['B'] =", config.fee_to_burn['B'])
            return False
        if float(instance_A.balances[coin1]) > maker_a and float(instance_A.balances['Wallet']) > 0.05:
            # BALANCE MASTER OK
            # print("   side1", instance_A.side, "bal", coin1, "ok")
            if float(instance_B.balances[coin2]) > taker_a:
                # print("   side1", instance_B.side, "bal", coin2, "ok, TRUE")
                return True
            else:
                print("   side1", instance_B.side, "bal", coin2, "too low", instance_B.balances[coin2], "|", taker_a)
        else:
            print("   side1", instance_A.side, "bal", coin1, "too low", instance_A.balances[coin1], "|", maker_a,
                  "FALSE1")
        return False
    elif side == "side2":
        if config.fee_to_burn['A'] < 0.0151:
            print("out of fee_to_burn['A'] =", config.fee_to_burn['A'])
            return False
        if float(instance_B.balances[coin1]) > maker_a and float(instance_B.balances['Wallet']) > 0.05:
            if float(instance_A.balances[coin2]) > taker_a:
                return True
            else:
                print("   side2", instance_A.side, "bal", coin2, "too low", instance_A.balances[coin2], "|", taker_a)
        else:
            print("   side2", instance_B.side, "bal", coin1, "too low", instance_B.balances[coin1], "|", maker_a,
                  "FALSE2")
        return False


def calc_order_data(coin1, coin2):
    global order_price, maker_amount, taker_amount, coin1coin2_cexprice
    coin1coin2_cexprice = None
    btcusd_r = cex_get_btc_rate_from_orderbook("USD")
    if coin1 != 'DASH':
        coin1_rate = cex_get_btc_rate_from_orderbook(coin1)
    else:
        coin1_r_usd = scrap_price_cmc(coin1)
        coin1_rate = coin1_r_usd / btcusd_r
    if coin2 != 'DASH':
        coin2_rate = cex_get_btc_rate_from_orderbook(coin2)
    else:
        coin2_r_usd = scrap_price_cmc(coin2)
        coin2_rate = coin2_r_usd / btcusd_r
    coin1coin2_cexprice = coin1_rate / coin2_rate
    order_price = coin1coin2_cexprice * random.uniform((1 + price_multi - 0.02), (1 + price_multi + 0.02))
    instance_A_bal_c1 = float(instance_A.balances[coin1])
    instance_A_bal_c2 = float(instance_A.balances[coin2])
    instance_B_bal_c1 = float(instance_B.balances[coin1])
    instance_B_bal_c2 = float(instance_B.balances[coin2])
    c_order_size_coin1 = -1
    if test_mode is False:
        if instance_A_bal_c1 > size_min[coin1] and instance_B_bal_c2 > size_min[coin2]:
            if instance_A_bal_c1 > size_max[coin1]:
                c_order_size_coin1 = random.uniform(size_min[coin1], size_max[coin1])
            else:
                c_order_size_coin1 = random.uniform(size_min[coin1], instance_A_bal_c1 * 0.97)
        elif instance_A_bal_c2 > size_min[coin2] and instance_B_bal_c1 > size_min[coin1]:
            if instance_B_bal_c1 > size_max[coin1]:
                c_order_size_coin1 = random.uniform(size_min[coin1], size_max[coin1])
            else:
                c_order_size_coin1 = random.uniform(size_min[coin1], instance_B_bal_c1 * 0.97)
        else:
            print(
                "calc_order_data\n   " + coin1 + "/" + coin2 + ": insufficient balances A B\n   size_min[" + coin1 + "]:",
                size_min[coin1], "instance_A_bal_c1:", instance_A_bal_c1, "instance_B_bal_c1:", instance_B_bal_c1,
                "\n   size_min[" + coin2 + "]:", size_min[coin2], "instance_B_bal_c2:", instance_B_bal_c2,
                "instance_A_bal_c2:",
                instance_A_bal_c2)
            return False
        maker_amount = "{:.6f}".format(c_order_size_coin1)
        taker_amount = "{:.6f}".format(c_order_size_coin1 * order_price)
        count = 0
        while 1:
            count += 1
            print("calc_order_data:\n   count", count, coin1 + "/" + coin2, "maker_amount", maker_amount,
                  "taker_amount", taker_amount, "\n   order_price", order_price, "c1c2_cexprice", coin1coin2_cexprice)
            if count > 2:
                print("   count>2")
                return False
            if instance_A_bal_c1 * 0.98 > float(maker_amount) > size_min[coin1]:
                if instance_B_bal_c2 * 0.98 > float(taker_amount):
                    print("   ok")
                    return True
                else:
                    print("  ", instance_B.side, "bal.c2", coin2, "too low:", instance_B.balances[coin2], taker_amount)
                    if instance_B_bal_c2 > size_min[coin2]:
                        org_maker = maker_amount
                        org_taker = taker_amount
                        new_amount = instance_B_bal_c2 * 0.97
                        taker_amount = "{:.6f}".format(random.uniform(size_min[coin2], new_amount))
                        maker_amount = "{:.6f}".format(float(taker_amount) / order_price)
                        print("   resize maker amount maker from:", org_maker, "to:", maker_amount, "taker from:",
                              org_taker, "to:", taker_amount)
                    else:
                        print("   resize,", instance_B.side, "bal.c2 too low", coin2, instance_B_bal_c2 * 0.97,
                              size_min[coin2])
                        # return False
            else:
                print("  ", instance_A.side, "bal.c1", coin1, "too low: bal", instance_A_bal_c1, "maker_amount",
                      maker_amount,
                      "size_min[" + coin1 + "]", size_min[coin1])
            # else:
            if instance_B_bal_c1 * 0.98 > float(maker_amount) > size_min[coin1]:
                if instance_A_bal_c2 * 0.98 > float(taker_amount):
                    print("   ok")
                    return True
                else:
                    print("  ", instance_A.side, "bal.c2", coin2, "too low:", instance_A.balances[coin2], taker_amount)
                    if instance_A_bal_c2 > size_min[coin2]:
                        org_maker = maker_amount
                        org_taker = taker_amount
                        new_amount = instance_A_bal_c2 * 0.97
                        taker_amount = "{:.6f}".format(random.uniform(size_min[coin2], new_amount))
                        maker_amount = "{:.6f}".format(float(taker_amount) / order_price)
                        print("   resize maker amount maker from:", org_maker, "to:", maker_amount, "taker from:",
                              org_taker, "to:", taker_amount)
                    else:
                        print("   resize,", instance_A.side, "bal.c2 too low", coin2, instance_A_bal_c2 * 0.97,
                              size_min[coin2])
            else:
                print("  ", instance_B.side, "bal.c1", coin1, "too low: bal", instance_B_bal_c1, "maker_amount",
                      maker_amount,
                      "size_min[" + coin1 + "]", size_min[coin1])
    elif test_mode is True:
        if coin1 in config.test_amount and coin2 in config.test_amount:
            maker_amount = "{:.6f}".format(test_amount[coin1])
            order_price = coin1coin2_cexprice * random.uniform((1 + price_multi - 0.02), (1 + price_multi + 0.02))
            taker_amount = "{:.6f}".format(float(maker_amount) * order_price)
            return True
        else:
            print("test mode, no test_amount set in config.py for those coins")
            exit()


def check_coins_exist(coin_list):
    tokens_A = xb.dxGetLocalTokens("A")
    tokens_B = xb.dxGetLocalTokens("B")
    check_A = any(item in coin_list for item in tokens_A)
    check_B = any(item in coin_list for item in tokens_B)
    if check_A and check_B:
        return True
    else:
        return False


def scrap_price_cmc(coin):
    price_url = "https://coinmarketcap.com/currencies/" + coin.lower() + "/"
    coin_data = requests.get(price_url).text
    sep1 = coin_data.find('","price":') + 10
    sep2 = coin_data.find(',"priceCurrency"')
    print(price_url, sep1, sep2)
    if sep1 > 0 and sep2 > 0:
        price = float(coin_data[sep1:sep2])
    else:
        print("error with separators")
        exit()
    print(price)
    return price


def check_cloudchains_blockcounts():
    if cc_on:
        global ccblockcounts_logger_timer
        chainz_url = "https://chainz.cryptoid.info/explorer/api.dws?q=summary"
        cc_url = 'https://plugin-api.core.cloudchainsinc.com/height'
        dogecoin_url = 'https://dogechain.info/chain/Dogecoin/q/getblockcount'
        rvn_url = 'https://rvn.cryptoscope.io/api/getblockcount/'
        bch_url = 'https://api.fullstack.cash/v5/blockchain/getBlockCount'
        xsn_url = 'https://explorer.masternodes.online/currencies/XSN/'
        xsn = requests.get(xsn_url).text
        xsn_separator1 = xsn.find('Last block: ') + 12
        xsn_separator2 = xsn.find('<br />', xsn_separator1)
        xsn_blockcount = int(xsn[xsn_separator1:xsn_separator2].replace(',', ''))
        rvn_blockcount = int(requests.get(rvn_url).json()['blockcount'])
        doge_blockcount = int(requests.get(dogecoin_url).json())
        bch_blockcount = int(requests.get(bch_url).json())
        cc_blockcounts_dict = requests.get(cc_url).json()
        # print(cc_blockcounts_dict)
        # exit()
        chainz_summary = requests.get(chainz_url).json()
        now = datetime.now()
        date = now.strftime("%Y-%m-%d %H:%M:%S")
        print(date)
        msg = f"{'blockcounts:':<13} | {'  CC':<8} | {'CHAINZ':<8} | {'OTHER':<8} | {'VALID?'}"
        result_list = []
        result_list.append(msg)
        result_list.append('-------------------------------------------------------')
        for key in cc_blockcounts_dict['result']:
            msg = None
            if cc_blockcounts_dict['result'][key] is None:
                print(key, cc_blockcounts_dict['result'][key])
            else:
                cc_blockcount = int(cc_blockcounts_dict['result'][key])
                if key.lower() in chainz_summary:
                    chainz_blockcount = chainz_summary[key.lower()]['height']
                    if chainz_blockcount + 3 >= cc_blockcount >= chainz_blockcount - 3:
                        valid = True
                    else:
                        valid = False
                    msg = f"{key:<13} | {cc_blockcount:<8} | {chainz_blockcount:<8} | {'':<8} | {valid}"
                    result_list.append(msg)
                else:
                    if key == 'DOGE':
                        if doge_blockcount + 3 >= cc_blockcount >= doge_blockcount - 3:
                            valid = True
                        else:
                            valid = False
                        msg = f"{key:<13} | {cc_blockcount:<8} | {'':<8} | {doge_blockcount:<8} | {valid}"
                        result_list.append(msg)
                    elif key == 'RVN':
                        if rvn_blockcount + 3 >= cc_blockcount >= rvn_blockcount - 3:
                            valid = True
                        else:
                            valid = False
                        msg = f"{key:<13} | {cc_blockcount:<8} | {'':<8} | {rvn_blockcount:<8} | {valid}"
                        result_list.append(msg)
                    elif key == 'BCH':
                        if bch_blockcount + 3 >= cc_blockcount >= bch_blockcount - 3:
                            valid = True
                        else:
                            valid = False
                        msg = f"{key:<13} | {cc_blockcount:<8} | {'':<8} | {bch_blockcount:<8} | {valid}"
                        result_list.append(msg)
                    elif key == 'XSN':
                        if xsn_blockcount + 3 >= cc_blockcount >= xsn_blockcount - 3:
                            valid = True
                        else:
                            valid = False
                        msg = f"{key:<13} | {cc_blockcount:<8} | {'':<8} | {xsn_blockcount:<8} | {valid}"
                        result_list.append(msg)
                    else:
                        if key != 'POLIS':
                            msg = f"{key:<13} | {cc_blockcount:<8} | {'':<8} | {'':<8} | {'?'}"
                            result_list.append(msg)
        if ccblockcounts_logger_timer == 0 or time.time() - ccblockcounts_logger_timer > ccblockcounts_logger_loop_timer:
            for each in result_list:
                blockcounts_logger.info(each)
            ccblockcounts_logger_timer = time.time()


def get_xbp2p_logs(start_date, end_date, id="", status=""):
    # DATE FORMAT datetime.now().strftime('%Y-%b-%d %H:%M:%S')
    date_xb_log_str = datetime.now().strftime('%Y%m%d')
    fp_xbridgep2p_log_A = config.chaindir_A + "/log/xbridgep2p_" + date_xb_log_str + ".log"
    fp_xbridgep2p_log_B = config.chaindir_B + "/log/xbridgep2p_" + date_xb_log_str + ".log"
    # print("paths:\n" + fp_xbridgep2p_log_A + '\n' + fp_xbridgep2p_log_B + '\n')
    log_A = []
    with open(fp_xbridgep2p_log_A, "r") as fileread:
        file = fileread.readlines()
    for line in file:
        if line[4:8].isnumeric():
            line_to_datetime = datetime.strptime(line[4:24], '%Y-%b-%d %H:%M:%S')
            # print(line_to_datetime, start_date, end_date)
            if start_date < line_to_datetime < end_date:
                # print("yes")
                log_A.append(line)
    log_B = []
    with open(fp_xbridgep2p_log_B, "r") as fileread:
        file = fileread.readlines()
    for line in file:
        if line[4:8].isnumeric():
            line_to_datetime = datetime.strptime(line[4:24], '%Y-%b-%d %H:%M:%S')
            # print(line_to_datetime, start_date, end_date)
            if start_date < line_to_datetime < end_date:
                # print("yes")
                log_B.append(line)
    a_file = id + "_" + status + "_A.log"
    b_file = id + "_" + status + "_B.log"
    textfile = open(a_file, "w")
    for each in log_A:
        textfile.write(each)
        # print(each)
    textfile.close()
    textfile = open(b_file, "w")
    for each in log_B:
        textfile.write(each)
        # print(each)
    textfile.close()
    zip_xbp2p_logs = zipfile.ZipFile("xbp2p.zip", "a", compression=zipfile.ZIP_DEFLATED, compresslevel=9)
    zip_xbp2p_logs.write(a_file)
    zip_xbp2p_logs.write(b_file)
    zip_xbp2p_logs.close()
    os.remove(a_file)
    os.remove(b_file)


# def play_my_sound(sound):
#     play(sound)

def main():
    global trade_counter, fail_count, flush_timer, maker_amount, taker_amount, order_price
    iteration = 0
    update_dex_bals(display=True)
    while 1:
        # CC API CHECK
        try:
            process = subprocess.Popen(['python3', 'cc-api-check/src/run.py'], stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT)
            process.wait()
        except Exception as e:
            print(e)
        # CC API CHECK
        iteration += 1
        # if iteration % 5 == 0 or iteration == 1:
        check_cloudchains_blockcounts()
        if not flush_timer or time.time() - flush_timer > flush_delay:
            print("flushing canceled orders")
            xb.dxFlushCancelledOrders("A")
            xb.dxFlushCancelledOrders("B")
            flush_timer = time.time()
        random.shuffle(markets)
        for market in markets:
            cancel_all_open_orders()
            org_trade_counter = trade_counter
            rand = random.randrange(0, 2)
            if rand == 1:
                # FLIP PAIRS RANDOMLY!
                coin1 = market[1]
                coin2 = market[0]
                instance_A.get_addresses(coin1, coin2)
                instance_B.get_addresses(coin1, coin2)
            else:
                coin1 = market[0]
                coin2 = market[1]
                instance_A.get_addresses(coin1, coin2)
                instance_B.get_addresses(coin1, coin2)
            usd_vol, usd_vol_s2 = get_pair_usd_volume(coin1, coin2)
            if usd_vol < usd_volume_target or test_mode and trade_counter != trade_to_do:
                print("rand:", rand, coin1 + "/" + coin2, "usd_vol:", usd_vol, "usd_vol_s2:", usd_vol_s2, "target:",
                      usd_volume_target)
                taking_timer = 0
                loop_timer = time.time()
                update_dex_bals()
                if coin1 in instance_A.balances and coin2 in instance_A.balances and coin1 in instance_B.balances and \
                        coin2 in instance_B.balances:
                    maker_amount = None
                    taker_amount = None
                    order_price = None
                    order_data_bol = calc_order_data(coin1, coin2)
                    if order_data_bol:
                        check_s1 = check_side_bal('side1', coin1, coin2)
                        check_s2 = check_side_bal('side2', coin1, coin2)
                        if check_s1 and check_s2:
                            if config.fee_to_burn['A'] > config.fee_to_burn['B'] and random.randrange(0, 2) == 1:
                                check_s1 = False
                                print("check_s1 modifier => false")
                        print("order_data_bol:\n   ", order_data_bol, "check_side_bal('side1')", check_s1,
                              "check_side_bal('side2')", check_s2)
                        if check_s1 and config.fee_to_burn['B'] >= 0.0151:
                            start_date = datetime.now() - time_delta
                            print("side1 A order maker:\n   from:", maker_amount, coin1, "to:", taker_amount, coin2,
                                  "@price:", order_price)
                            if not (check_coins_exist([coin1, coin2]) or check_coins_exist([coin1, coin2])):
                                print("check_coins_exist A B failed!")
                                exit()
                                break
                            else:
                                print("check_coins_exist A B ok!")
                            if config.test_partial and config.test_mode:
                                partial_amount = "{:.6f}".format(float(maker_amount) / 2)
                                msg = "A.DxMakePartialOrder( " + coin1 + ", " + str(maker_amount) + ", " + \
                                      instance_A.coin_address_list[
                                          coin1] + ", " + coin2 + ", " + str(taker_amount) + ", " + \
                                      instance_A.coin_address_list[
                                          coin2] + ", " + partial_amount + ", " + "False )"
                                maker_order = xb.dxMakePartialOrder("A", coin1, maker_amount,
                                                                    instance_A.coin_address_list[coin1],
                                                                    coin2, taker_amount,
                                                                    instance_A.coin_address_list[coin2],
                                                                    partial_amount, False)
                            else:
                                msg = "A.DxMakeOrder( " + coin1 + ", " + str(maker_amount) + ", " + \
                                      instance_A.coin_address_list[
                                          coin1] + ", " + coin2 + ", " + str(taker_amount) + ", " + \
                                      instance_A.coin_address_list[
                                          coin2] + " )"
                                maker_order = xb.dxMakeOrder("A", coin1, maker_amount,
                                                             instance_A.coin_address_list[coin1],
                                                             coin2, taker_amount,
                                                             instance_A.coin_address_list[coin2])
                            trade_logger.info(msg)
                            print(maker_order)
                            order_timer = time.time()
                            time.sleep(1)
                            if 'id' not in maker_order:
                                print("error with order\n", maker_order)
                                exit()
                            if wait_created_order(maker_order['id'], "A"):
                                msg = "B.DxTakeOrder( " + maker_order['id'] + ", " + instance_B.coin_address_list[
                                    coin2] + ", " + \
                                      instance_B.coin_address_list[coin1] + " )"
                                trade_logger.info(msg)
                                taker_order = xb.dxTakeOrder("B", maker_order['id'],
                                                             instance_B.coin_address_list[coin2],
                                                             instance_B.coin_address_list[coin1])
                                taking_timer = time.time()
                                time.sleep(1)
                                if 'code' in taker_order:
                                    trade_logger.critical(taker_order)
                                else:
                                    taker_order = xb.getorderstatus("B", maker_order['id'])
                                    counter = 0
                                    fail_open_count = 0
                                    done = 0
                                    display_timer = 0
                                    display_delay = 10
                                    while done == 0:
                                        counter += 1
                                        if display_timer == 0 or time.time() - display_timer > display_delay:
                                            print("in progress: A.maker_status:", [maker_order['status']],
                                                  "B.taker_status:",
                                                  [taker_order['status']])
                                            display_timer = time.time()
                                        if "initialized" in taker_order['status']:
                                            if time.time() - taking_timer > max_delay_initialized:
                                                xb.cancelorder("A", maker_order['id'])
                                                msg = "B.Taker status stuck on 'initialized', A.cancel " + maker_order[
                                                    'id']
                                                trade_logger.critical(msg)
                                                time.sleep(1)
                                                # taker_order = xb.getorderstatus("B", maker_order['id'])
                                                break
                                        elif "open" in taker_order['status']:
                                            fail_open_count += 1
                                            if fail_open_count == 3:
                                                xb.cancelorder("A", maker_order['id'])
                                                msg = "open while taken, A.cancel " + maker_order['id']
                                                trade_logger.critical(msg)
                                                time.sleep(1)
                                                maker_order = xb.getorderstatus("A", maker_order['id'])
                                                break
                                            time.sleep(0.5)
                                            xb.dxTakeOrder("B", maker_order['id'], instance_B.coin_address_list[coin2],
                                                           instance_B.coin_address_list[coin1])
                                            print(msg)
                                            time.sleep(0.5)
                                        elif "finished" in taker_order['status']:
                                            trade_counter += 1
                                            total_trade_time.append(time.time() - taking_timer)
                                            done = 1
                                            update_fee_count('B')
                                            # play_my_sound(sound1)
                                            # CC API CHECK
                                            try:
                                                process = subprocess.Popen(['python3', 'cc-api-check/src/run.py'],
                                                                           stdout=subprocess.DEVNULL,
                                                                           stderr=subprocess.STDOUT)
                                                process.wait()
                                            except Exception as e:
                                                print(e)
                                            # CC API CHECK
                                        elif check_status_fail(taker_order['status']):
                                            msg = "error with order: " + maker_order['id'] + ", " + taker_order[
                                                'status']
                                            trade_logger.critical(msg)
                                            update_fee_count('B')
                                            end_date = datetime.now()
                                            try:
                                                get_xbp2p_logs(start_date, end_date, maker_order['id'],
                                                               taker_order['status'])
                                            except Exception as e:
                                                print(e)
                                            exit()
                                        time.sleep(1)
                                        maker_order = xb.getorderstatus("A", maker_order['id'])
                                        taker_order = xb.getorderstatus("B", maker_order['id'])
                                    msg = "done! " + maker_order['id'] + ", " + taker_order['status']
                                    trade_logger.info(msg)
                                    time.sleep(2)
                                    end_date = datetime.now()
                                    try:
                                        get_xbp2p_logs(start_date, end_date, maker_order['id'], taker_order['status'])
                                    except Exception as e:
                                        print(e)
                                # MASTER SELL COIN1 FOR COIN2, SLAVE BUY COIN1 WITH COIN 2
                            else:
                                print('wait_created_order(' + maker_order['id'] + ', "A") FAILED')
                                end_date = datetime.now()
                                try:
                                    get_xbp2p_logs(start_date, end_date, maker_order['id'], "son")
                                except Exception as e:
                                    print(e)
                        elif check_s2 and config.fee_to_burn['A'] >= 0.0151:
                            start_date = datetime.now() - time_delta
                            print("side2 B order maker:\n   from:", maker_amount, coin1, "to:", taker_amount, coin2,
                                  "@price:", order_price)
                            if not (check_coins_exist([coin1, coin2]) or check_coins_exist([coin1, coin2])):
                                print("check_coins_exist A B failed!")
                                exit()
                                break
                            else:
                                print("check_coins_exist A B ok!")
                            if config.test_partial and config.test_mode:
                                partial_amount = "{:.6f}".format(float(maker_amount) / 2)
                                msg = "B.DxMakePartialOrder( " + coin1 + ", " + str(maker_amount) + ", " + \
                                      instance_B.coin_address_list[coin1] + ", " + coin2 + ", " + str(
                                    taker_amount) + ", " + \
                                      instance_B.coin_address_list[coin2] + ", " + partial_amount + ", " + "False )"
                                partial_amount = "{:.6f}".format(float(maker_amount) / 2)

                                maker_order = xb.dxMakePartialOrder("B", coin1, maker_amount,
                                                                    instance_B.coin_address_list[coin1],
                                                                    coin2, taker_amount,
                                                                    instance_B.coin_address_list[coin2],
                                                                    partial_amount, False)

                            else:
                                msg = "B.DxMakeOrder( " + coin1 + ", " + str(maker_amount) + ", " + \
                                      instance_B.coin_address_list[
                                          coin1] + ", " + coin2 + ", " + str(taker_amount) + ", " + \
                                      instance_B.coin_address_list[
                                          coin2] + " )"
                                maker_order = xb.dxMakeOrder("B", coin1, maker_amount,
                                                             instance_B.coin_address_list[coin1],
                                                             coin2, taker_amount, instance_B.coin_address_list[coin2])
                            trade_logger.info(msg)
                            print(maker_order)
                            # MOD SIDE2
                            order_timer = time.time()
                            time.sleep(1)
                            if 'id' not in maker_order:
                                print("error with order\n", maker_order)
                                exit()
                            if wait_created_order(maker_order['id'], "B"):
                                msg = "A.DxTakeOrder( " + maker_order['id'] + ", " + instance_A.coin_address_list[
                                    coin2] + ", " + \
                                      instance_A.coin_address_list[coin1] + " )"
                                trade_logger.info(msg)

                                taker_order = xb.dxTakeOrder("A", maker_order['id'],
                                                             instance_A.coin_address_list[coin2],
                                                             instance_A.coin_address_list[coin1])
                                taking_timer = time.time()
                                time.sleep(1)
                                if 'code' in taker_order:
                                    trade_logger.critical(taker_order)
                                else:
                                    taker_order = xb.getorderstatus("A", maker_order['id'])
                                    counter = 0
                                    fail_open_count = 0
                                    done = 0
                                    display_timer = 0
                                    display_delay = 10
                                    while done == 0:
                                        counter += 1
                                        if display_timer == 0 or time.time() - display_timer > display_delay:
                                            print("in progress: B.maker_status:", [maker_order['status']],
                                                  "A.taker_status:",
                                                  [taker_order['status']])
                                            display_timer = time.time()
                                        if "initialized" in taker_order['status']:
                                            if time.time() - taking_timer > max_delay_initialized:
                                                xb.cancelorder("B", maker_order['id'])
                                                msg = "A.Taker status stuck on 'initialized', B.cancel " + maker_order[
                                                    'id']
                                                trade_logger.critical(msg)
                                                time.sleep(1)
                                                # taker_order = xb.getorderstatus("A", maker_order['id'])
                                                break
                                        elif "open" in taker_order['status']:
                                            fail_open_count += 1
                                            if fail_open_count == 3:
                                                xb.cancelorder("B", maker_order['id'])
                                                e_msg = "open while taken, B.cancel " + maker_order['id']
                                                # print(msg)
                                                trade_logger.critical(e_msg)
                                                time.sleep(1)
                                                maker_order = xb.getorderstatus("B", maker_order['id'])
                                                break
                                            time.sleep(0.5)
                                            xb.dxTakeOrder("A", maker_order['id'], instance_A.coin_address_list[coin2],
                                                           instance_A.coin_address_list[coin1])
                                            print(msg)
                                            time.sleep(0.5)
                                        elif "finished" in taker_order['status']:
                                            trade_counter += 1
                                            total_trade_time.append(time.time() - taking_timer)
                                            done = 1
                                            update_fee_count('A')
                                            # play_my_sound(sound1)
                                            # CC API CHECK
                                            try:
                                                process = subprocess.Popen(['python3', 'cc-api-check/src/run.py'],
                                                                           stdout=subprocess.DEVNULL,
                                                                           stderr=subprocess.STDOUT)
                                                process.wait()
                                            except Exception as e:
                                                print(e)
                                            # CC API CHECK
                                        elif check_status_fail(taker_order['status']):
                                            msg = "error with order: " + maker_order['id'] + ", " + taker_order[
                                                'status']
                                            trade_logger.critical(msg)
                                            update_fee_count('A')
                                            end_date = datetime.now()
                                            try:
                                                get_xbp2p_logs(start_date, end_date, maker_order['id'],
                                                               taker_order['status'])
                                            except Exception as e:
                                                print(e)
                                            exit()
                                        time.sleep(1)
                                        taker_order = xb.getorderstatus("A", maker_order['id'])
                                        maker_order = xb.getorderstatus("B", maker_order['id'])
                                    msg = "done!" + maker_order['id'] + ", " + taker_order['status']
                                    trade_logger.info(msg)
                                    time.sleep(2)
                                    end_date = datetime.now()
                                    try:
                                        get_xbp2p_logs(start_date, end_date, maker_order['id'], taker_order['status'])
                                    except Exception as e:
                                        print(e)
                            else:
                                print('wait_created_order(' + maker_order['id'] + ', "B") FAILED')
                                end_date = datetime.now()
                                try:
                                    get_xbp2p_logs(start_date, end_date, maker_order['id'], 'son')
                                except Exception as e:
                                    print(e)
                                # SLAVE SELL COIN1 FOR COIN2, MASTER BUY COIN1 WITH COIN 2
                    else:
                        print("order_data_bol", order_data_bol)
                else:
                    print("COIN MISSING IN BALANCES!!", instance_A.balances, instance_B.balances)
                    fail_count += 1
                    if fail_count % 10 == 0:
                        print("dxloadxbridgeconf A", xb.dxloadxbridgeconf("A"))
                        print("dxloadxbridgeconf B", xb.dxloadxbridgeconf("B"))
                if org_trade_counter != trade_counter:
                    msg = "order_exec_time: " + str(total_trade_time[-1]) + ", average: " + str(
                        sum(total_trade_time) / len(total_trade_time)) + ", trade_counter: " + str(trade_counter)
                    # print(msg)
                    trade_logger.info(msg)
                    sleep_timer = time.time()
                    trade_delay_current = random.uniform(trade_delay * 0.85, trade_delay * 1.15)
                    if test_mode is False and trade_counter == trade_to_do or test_mode is True and trade_counter == test_trade_to_do:
                        print("trade_to_do reached:", trade_counter)
                        exit()
                    print("trade executed, sleep", trade_delay_current, "secs")
                    while time.time() - sleep_timer < trade_delay_current:
                        print("*", end='')
                        time.sleep(5)
                    print("\nSleep done")
                usd_vol, usd_vol_s2 = get_pair_usd_volume(coin1, coin2)
            if usd_vol > usd_volume_target:
                print(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), "| 24H USD Volume on", coin1 + "/" + coin2 + ":",
                      usd_vol, usd_vol_s2, "| target:", usd_volume_target, "reached.\n")
            else:
                print(datetime.now().strftime('%Y-%m-%d_%H:%M:%S'), "| 24H USD Volume on", coin1 + "/" + coin2 + ":",
                      usd_vol, usd_vol_s2, "| target:", usd_volume_target, "in progress.\n")

        print("***loop_done***")
        # time.sleep(10)
        print("")
        update_dex_bals(display=True)
