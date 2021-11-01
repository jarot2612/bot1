import web3, json, os, time, sys, datetime, requests
from web3 import Web3
from config import setup
from decimal import Decimal

class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


web3 = Web3(Web3.HTTPProvider('https://rpc.ftm.tools/')) #NODE RPC CHAIN 

spender = Web3.toChecksumAddress('0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83') 
factory = Web3.toChecksumAddress('0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3')#FACTORY ADDRESS PANCAKESWAP

router = Web3.toChecksumAddress('0xF491e7B69E4244ad4002BC14e878a34207E38c29')#ROUTER ADDRESS PANCAKESWAP
  
#ABICODE PANCAKE ROUTER, BEP20, PANCAKE FACTORY
routers = setup['routerABI']
factorys = setup['factoryABI']
bep20 = setup['bep20']
  
wallet = Web3.toChecksumAddress('0x13c59dd4e2d509752949d5a917359b6a75995edd')
private_key = "d798643a69d68da0ca389812b87e14c83a15b8290d6e121ea8118a3130dc73e0"

amounts = Web3.toWei(2, unit='ether')
gasAmount = int(1000000)
gasPrice = Web3.toWei(1500, unit='gwei')
slippage = int(49)
transaction = int(10000)#DON'T CHANGE

routers = web3.eth.contract(abi = routers, address = router) #GET FUNCTION 
factorys = web3.eth.contract(abi = factorys, address = factory)#GET FUNCTION
Erc = web3.eth.contract(abi = bep20, address = spender)#GET FUNCTION

timeStampData = datetime.datetime.now()
currentTimeStamp = timeStampData.strftime("%H:%M:%S")[:-3]
    
def print_slow(str):
  for letter in str:
    sys.stdout.write(letter)
    sys.stdout.flush()
    time.sleep(0.1)

def delete_last_line():
  sys.stdout.write('\x1b[1A')
  sys.stdout.write('\x1b[2K')
  
if web3.isConnected():
  print_slow(style.YELLOW+"Web3 is connected | FANTOM OPERA\n"+style.RESET)
  print("")

balance_account = web3.eth.get_balance(wallet)/ 10**18

print_slow(style.YELLOW+"Connected wallet address {}".format(wallet[:15]) +"...\nBal: {:.4f}".format(balance_account)+ " FTM | Amount: {:.4f}".format(amounts/10**18)+" BNB | Slip: {}".format(slippage)+"% "+style.RESET)
print("")
print("")

inputToken = input(style.YELLOW+"Submit your token address here : "+style.RESET)
  
token_address = Web3.toChecksumAddress(inputToken)
print("")

#CLASS CONTRACT FOR TOKEN ADDRESS 
tokens = web3.eth.contract(abi = bep20, address = token_address)
symbol = tokens.functions.symbol().call()
dec = tokens.functions.decimals().call()

#FUNCTION BUY TOKEN
def buy_token():
  get_amounts = routers.functions.getAmountsOut(amounts, [spender, token_address]).call()[-1]
  min_slippage = (Decimal(100) - Decimal(slippage)) / Decimal(100)
  min_amount = "{:.0f}".format(min_slippage * get_amounts)
  
  count = web3.eth.get_transaction_count(wallet)
  
  buy = routers.functions.swapExactETHForTokens(
    int(min_amount),
    [spender, token_address],
    wallet,
    (int(time.time()+transaction))
    ).buildTransaction({
      "from" : wallet,
      "value" : amounts,
      "gas" : gasAmount,
      "gasPrice": gasPrice,
      "nonce": count
    })
  
  buying = web3.eth.account.sign_transaction(buy, private_key)
  
  raw_tx = web3.eth.send_raw_transaction(buying.rawTransaction)
  hashes = Web3.toHex(raw_tx)
  time.sleep(8)
  status = web3.eth.get_transaction_receipt(hashes)
  txStatus = status.status
   
  if int(txStatus) == 1:
    
    print(style.YELLOW+"SuccessFully Bought {:.2f}".format(float(min_amount/10**dec))+" $symbol at transactionHash {}".format(hashes)+style.RESET)
    
  else:
    
    print(style.MAGENTA+"TRANSACTION FAILED !!"+style.RESET)
    
while True:
  try:
    pair = factorys.functions.getPair(spender, token_address).call()
    balPair = Erc.functions.balanceOf(pair).call() /10**18
    
    if pair == '0x0000000000000000000000000000000000000000':
      print_slow(style.MAGENTA+"~ Searching Pair Address for token ${}".format(symbol)+style.RESET+"\n")
      delete_last_line()
    elif pair != "0x0000000000000000000000000000000000000000" and balPair > 0:
      buy_token()
      break
    
    elif pair == '0x0000000000000000000000000000000000000000':
      print_slow(style.MAGENTA+"~ Searching Pair Address for token ${}".format(symbol)+style.RESET+"\n")
      delete_last_line()

    else:
      print_slow(style.MAGENTA+"~ Insuciffient Liquidity for ${}".format(symbol)+"/WBNB pair address!!\n"+style.RESET)
      delete_last_line()
    
  except Exception as e:
    print(e)