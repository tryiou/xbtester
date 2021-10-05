# chaindir used to pick xbp2plog extract from chaindir/log/ store each order data in xbp2p.zip
chaindir_A = "/home/user/.blocknetA"
chaindir_B = "/home/user/.blocknetB"
rpc_port_A = 41100
rpc_port_B = 41200
rpc_user = 'BlockDXBlocknet'
rpc_password = 'pass'

# test mode
test_mode = False
test_partial = False
t_markets = [["BLOCK", "LTC"]]
test_trade_to_do = 1
test_amount = {}
test_amount["BLOCK"] = 0.1
test_amount["LTC"] = 0.001642
test_amount["DGB"] = 2
test_amount["RVN"] = 1.3
test_amount["PIVX"] = 0.2
# test mode


trade_delay = 60 * 5  # seconds, time to wait between each trade (randomised)
price_multi = 0.05  # increase cex price by this %ratio
usd_volume_target = 2000
trade_to_do = 1000
trade_to_do_daily = 205
slow_down_modifier = 4  # once trade_to_do_daily reached, delay per trade = trade_delay * slow_down_modifier
n_markets = [["BLOCK", "DASH"], ["BLOCK", "LTC"], ["BLOCK", "RVN"], ["DASH", "LTC"], ["BLOCK", "PIVX"],
             ["BLOCK", "SYS"]]  # ,["BLOCK", "PIVX"], ["LTC", "PIVX"]]

cc_on = False  # if set to true, check cc api height and compare to external source, print to terminal, no action
email_send = False # if set to true, send mail to mail_destination if detecting cc chains on wrong height
mail_log = "login"
mail_pass = "pass"
mail_destination = "destination@mail.com"

size_max = {}
size_max['BLOCK'] = 100
size_max['LTC'] = 0.6
size_max['SYS'] = 550
size_max['DASH'] = 0.9
size_max['PIVX'] = 100
size_max['LBC'] = 2500
size_max['DGB'] = 800
size_max['RVN'] = 900
size_max['SYS'] = 300

size_min = {}
size_min['BLOCK'] = size_max['BLOCK'] / 3
size_min['LTC'] = size_max['LTC'] / 2
size_min['SYS'] = size_max['SYS'] / 2
size_min['DASH'] = size_max['DASH'] / 3
size_min['PIVX'] = size_max['PIVX'] / 2
size_min['LBC'] = size_max['LBC'] / 2
size_min['DGB'] = size_max['DGB'] / 2
size_min['RVN'] = size_max['RVN'] / 2
size_min['SYS'] = size_max['SYS'] / 2


# IF NO ADDRESS SET FOR A COIN, BOT WILL GATHER NEW ONE AND REGISTER HERE, DONT CHANGE THIS PART

dx_addresses_A = {}

dx_addresses_B = {}

# TAKER FEE POOL
fee_to_burn = {}
fee_to_burn['A'] = 10
fee_to_burn['B'] = 10
