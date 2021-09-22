import dxbottools_A, dxbottools_B
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
            print(type(e), e)
            time.sleep(4 * count)
        else:
            return result


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
            print(type(e), e)
        else:
            return result


def dxgetorderfills(side, c1, c2, reverse: bool):
    print("dxgetorderfills(", c1, c2, reverse, ")")
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
            print(type(e), e)
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
            print(type(e), e)
        else:
            return result


def getorderstatus(side, id):
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
                result = dxbottools_A.getorderstatus(id)
            if side == "B":
                result = dxbottools_B.getorderstatus(id)
        except Exception as e:
            print(type(e), e)
        else:
            return result


def cancelorder(side, id):
    done = False
    count = 0
    result = None
    while not done:
        count += 1
        if count == max_count:
            print(side, "cancelorder max_count reached")
            exit()
        try:
            if side == "A":
                result = dxbottools_A.cancelorder(id)
            if side == "B":
                result = dxbottools_B.cancelorder(id)
        except Exception as e:
            print(type(e), e)
        else:
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
            print(type(e), e)
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
            print(type(e), e)
        else:
            return result


def dxMakePartialOrder(side, coin1, maker_amount, maker_address, coin2, taker_amount, taker_address, partial_amount,
                       repost: bool):
    done = False
    count = 0
    result = None
    # print(type(coin1), coin1, type(maker_amount), maker_amount, type(maker_address), maker_address, type(coin2), coin2,
    #       type(taker_amount), taker_amount, type(taker_address), taker_address, type(partial_amount), partial_amount,
    #       type(str(repost)), str(repost))
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
            print(type(e), e)
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
            print(type(e), e)
        else:
            return result


def dxTakeOrder(side, id, maker_address, taker_address):
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
                result = dxbottools_A.takeorder(id, maker_address, taker_address)
            if side == "B":
                result = dxbottools_B.takeorder(id, maker_address, taker_address)
        except Exception as e:
            print(type(e), e)
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
            print(type(e), e)
        else:
            return result
