import dxbottools_A
import dxbottools_B
import time

max_count = 10


def dxloadxbridgeconf(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxloadxbridgeconf max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxloadxbridgeconf()
            if side == "B":
                result = dxbottools_B.rpc_connection.dxloadxbridgeconf()
        except Exception as e:
            print("dxloadxbridgeconf", type(e), e)
            time.sleep(4 * count)
        else:
            return result


def xrGetBlockCount(side, coin, node_count=1):
    done = False
    count = 0
    result = None
    max_count = 2
    while not done:
        count += 1
        if count == max_count:
            print(side, "xrGetBlockCount max_count reached")
            return None
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.xrGetBlockCount(coin, node_count)
            if side == "B":
                result = dxbottools_B.rpc_connection.xrGetBlockCount(coin, node_count)
            test = result['reply']
        except Exception as e:
            print("xrGetBlockCount", side, coin, node_count, '\n', type(e), e)
            time.sleep(4 * count)
        else:
            return result['reply']


def xrGetNetworkServices(side):
    done = False
    count = 0
    result = None
    max_count = 2
    while not done:
        count += 1
        if count == max_count:
            # print(side, "xrGetNetworkServices max_count reached")
            return None
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.xrGetNetworkServices()
            if side == "B":
                result = dxbottools_B.rpc_connection.xrGetNetworkServices()
            test = result['reply']
        except Exception as e:
            print("xrGetNetworkServices", side, type(e), e)
            time.sleep(4 * count)
        else:
            return result['reply']


def getnetworkinfo(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "getnetworkinfo max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.getnetworkinfo()
            if side == "B":
                result = dxbottools_B.rpc_connection.getnetworkinfo()
        except Exception as e:
            print("getnetworkinfo", type(e), e)
        else:
            return result


def dxgetorderfills(side, c1, c2, reverse: bool):
    # print("dxgetorderfills(", c1, c2, reverse, ")")
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxgetorderfills max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxgetorderfills(c1, c2, reverse)
            if side == "B":
                result = dxbottools_B.rpc_connection.dxgetorderfills(c1, c2, reverse)
        except Exception as e:
            print("dxgetorderfills", type(e), e)
        else:
            return result


def dxGetTokenBalances(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxGetTokenBalances max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxGetTokenBalances()
            if side == "B":
                result = dxbottools_B.rpc_connection.dxGetTokenBalances()
        except Exception as e:
            print("dxGetTokenBalances", type(e), e)
        else:
            return result


def getorderstatus(side, order_id):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "getorderstatus max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.getorderstatus(order_id)
            if side == "B":
                result = dxbottools_B.getorderstatus(order_id)
        except Exception as e:
            print("getorderstatus", type(e), e)
        else:
            return result


def cancelorder(side, order_id):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print("Failed cancelling", side, order_id)
            exit()
        try:
            status = []
            if side == "A":
                result = dxbottools_A.cancelorder(order_id)
                time.sleep(0.25)
                status = dxbottools_A.getorderstatus(order_id)
            elif side == "B":
                result = dxbottools_B.cancelorder(order_id)
                time.sleep(0.25)
                status = dxbottools_B.getorderstatus(order_id)
            if 'status' in status and "canceled" in status['status']:
                done = True
            else:
                time.sleep(0.25)
        except Exception as e:
            print("cancelorder", type(e), e)
    # print(result)
    return result


def getopenorders(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "getopenorders max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.getopenorders()
            if side == "B":
                result = dxbottools_B.getopenorders()
        except Exception as e:
            print(type(e), e)
        else:
            return result


def dxGetLocalTokens(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxGetLocalTokens max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxGetLocalTokens()
            if side == "B":
                result = dxbottools_B.rpc_connection.dxGetLocalTokens()
        except Exception as e:
            print("dxGetLocalTokens", type(e), e)
        else:
            return result


def dxFlushCancelledOrders(side):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxFlushCancelledOrders max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxFlushCancelledOrders(0)
            if side == "B":
                result = dxbottools_B.rpc_connection.dxFlushCancelledOrders(0)
        except Exception as e:
            print("dxFlushCancelledOrders", type(e), e)
        else:
            return result


def dxMakePartialOrder(side, coin1, maker_amount, maker_address, coin2, taker_amount, taker_address, partial_amount,
                       repost: bool):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxMakePartialOrder max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxMakePartialOrder(coin1, maker_amount, maker_address,
                                                                        coin2, taker_amount, taker_address,
                                                                        partial_amount, str(repost))
            if side == "B":
                result = dxbottools_B.rpc_connection.dxMakePartialOrder(coin1, maker_amount, maker_address,
                                                                        coin2, taker_amount, taker_address,
                                                                        partial_amount, str(repost))
        except Exception as e:
            if count + 1 == max_count:
                print("dxMakePartialOrder(", side, coin1, maker_amount, maker_address, coin2, taker_amount,
                      taker_address,
                      partial_amount, repost, ")", )
            print("dxMakePartialOrder", type(e), e)
        else:
            return result


def dxMakeOrder(side, coin1, maker_amount, maker_address, coin2, taker_amount, taker_address):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxMakeOrder max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.rpc_connection.dxMakeOrder(coin1, maker_amount, maker_address,
                                                                 coin2, taker_amount, taker_address, 'exact')
            if side == "B":
                result = dxbottools_B.rpc_connection.dxMakeOrder(coin1, maker_amount, maker_address,
                                                                 coin2, taker_amount, taker_address, 'exact')
        except Exception as e:
            print("dxMakeOrder", type(e), e)
        else:
            return result


def dxTakeOrder(side, order_id, maker_address, taker_address):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "dxTakeOrder max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.takeorder(order_id, maker_address, taker_address)
            if side == "B":
                result = dxbottools_B.takeorder(order_id, maker_address, taker_address)
        except Exception as e:
            print("dxTakeOrder", type(e), e)
        else:
            return result


def getnewtokenadress(side, coin):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "getnewtokenadress max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.getnewtokenadress(coin)
            if side == "B":
                result = dxbottools_B.getnewtokenadress(coin)
        except Exception as e:
            print("getnewtokenadress", type(e), e)
        else:
            return result
