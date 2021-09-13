# USED TO EXTRACT XB P2P LOG
chaindir_A = "/home/user/.blocknetA"
chaindir_B = "/home/user/.blocknetB"

# USED TO SEND RPC CALL TO EACH XB INSTANCE
rpc_port_A = 41100
rpc_port_B = 41200
# A & B should be set with same RPC user & pass
rpc_user = 'BlockDXBlocknet'
rpc_password = 'mypass'

# test mode
# if set to True, disable regular behavior and use only test config:
test_mode = False
# if partial set to True, maker will create a partial order with min_size = ordersize / 2 and repost at False
test_partial = False
t_markets = [["BLOCK", "DGB"]]
test_trade_to_do = 5
test_amount = {}
test_amount["BLOCK"] = 0.1
test_amount["LTC"] = 0.0006910
test_amount["DGB"] = 2
# test mode

# seconds, time to wait between each trade (randomised)
trade_delay = 60 * 5

# increase cex price by this %ratio
price_multi = 0.05
usd_volume_target = 2000
trade_to_do = 1000
n_markets = [["BLOCK", "DASH"], ["BLOCK", "PIVX"], ["BLOCK", "LTC"], ["BLOCK", "RVN"], ["LTC", "PIVX"]]

# if set to true, check cc api height and compare to external source, print to terminal, no action
cc_on = False


# order size is randomized between size min and size max
size_max = {}
size_max['BLOCK'] = 100
size_max['LTC'] = 0.6
size_max['SYS'] = 550
size_max['DASH'] = 0.9
size_max['PIVX'] = 100
size_max['LBC'] = 2500
size_max['DGB'] = 800
size_max['RVN'] = 600

size_min = {}
size_min['BLOCK'] = size_max['BLOCK'] / 4
size_min['LTC'] = size_max['LTC'] / 2
size_min['SYS'] = size_max['SYS'] / 2
size_min['DASH'] = size_max['DASH'] / 3
size_min['PIVX'] = size_max['PIVX'] / 2
size_min['LBC'] = size_max['LBC'] / 2
size_min['DGB'] = size_max['DGB'] / 2
size_min['RVN'] = size_max['RVN'] / 2

# IF NO ADDRESS SET FOR A COIN, BOT WILL GATHER NEW ONE AND REGISTER HERE, DONT CHANGE STRUCURE/DONT ADD COMMENTS TO THOSE LINES!
dx_addresses_A = {}

dx_addresses_B = {}


# TAKER FEE POOL, BLOCK TO BURN INTO FEE
fee_to_burn = {}
fee_to_burn['A'] = 10
fee_to_burn['B'] = 10
