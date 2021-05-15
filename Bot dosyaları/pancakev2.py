from web3 import Web3
import json
import time
from var_p_v2 import keys, contract_keys


#web3 = Web3(Web3.HTTPProvider("https://bsc.nownodes.io/?API_key=39OW8tlrbf0wL7ORTeXwEFJ5RHHBVyHf"))
web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
#web3 = Web3(Web3.WebsocketProvider("wss://bsc-ws-node.nariox.org:443"))

print (web3.eth.getBalance("0xB075076c7A58c9FF84959783e9EB5896aA597a6c")/1000000000000000000)

address= Web3.toChecksumAddress("0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73")
abi=json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[],"name":"INIT_CODE_PAIR_HASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
buy_token = Web3.toChecksumAddress (contract_keys["buy_token"])
bnb_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

contract= web3.eth.contract(address=address,abi=abi)

event_filter = contract.events.PairCreated.createFilter(fromBlock="latest")





#pair = Web3.toChecksumAddress ("0xaf31fd9c3b0350424bf96e551d2d1264d8466205")


# uniswap contract 
pancakeswap_contract_abi = json.loads(contract_keys["pancakeswap_abi"])
pancakeswap_contract_address = Web3.toChecksumAddress(contract_keys["pancakeswap_address"])
pancakeswap_contract = web3.eth.contract(address=pancakeswap_contract_address, abi=pancakeswap_contract_abi)


bnb_contract_abi = json.loads(contract_keys["bnb_abi"])
bnb_contract_address = Web3.toChecksumAddress(contract_keys["bnb_token"])
bnb_contract = web3.eth.contract(address=bnb_contract_address, abi=bnb_contract_abi)
kif_contract_abi = json.loads(contract_keys["kif_abi"])
kif_contract_address = Web3.toChecksumAddress(contract_keys["buy_token"])
kif_contract = web3.eth.contract(address=kif_contract_address, abi=kif_contract_abi)




# contracts used in path, eth->weth->kif and kif->weth->eth



#print(list(pancakeswap_contract.functions))


def buy_kif(eth_out: int, slippage: float, receiver: str):
    path = [Web3.toChecksumAddress(contract_keys["bnb_token"]), Web3.toChecksumAddress(contract_keys["buy_token"])] 
    amountOutMin = int(eth_out * get_price_eth_to_kif() * (1 - slippage))*1000000000000000000
    to = receiver
    deadline = int(time.time()) + 220 # added 120 seconds from when the transaction was sent
    txn = pancakeswap_contract.functions.swapExactETHForTokens(amountOutMin=amountOutMin, path=path, to=to, deadline=deadline).buildTransaction({
        'nonce': web3.eth.getTransactionCount(keys["my_account"]),
        'value': web3.toWei(eth_out, 'ether'),
        'gas': keys["gas_limit"],
        'gasPrice':web3.toWei(keys["gas_price"], 'gwei')})
    signed_tx = web3.eth.account.signTransaction(txn, keys["private_key"])
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(web3.toHex(tx_hash))
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("buy successful")
    print("one kif is worth this much eth: " + str(get_price_kif_to_eth()))
    
# kif_out: the amount of kif you want to exchange for eth
# slippage: percentage tolerance for tokens in/out
# receiver: the receiving address of the final tokens
### this function turns your kif->weth->eth
def sell_kif(kif_out: int, slippage: float, receiver: str):
    amountIn = kif_out
    amountOutMin = int(kif_out * get_price_kif_to_eth() * (1 - slippage))*1000000000000000000
    path = [Web3.toChecksumAddress(contract_keys["buy_token"]), Web3.toChecksumAddress(contract_keys["bnb_token"])] 
    to = receiver
    deadline = int(time.time()) + 220 # added 120 seconds from when the transaction was sent
    txn = pancakeswap_contract.functions.swapExactTokensForETH(amountIn=amountIn, amountOutMin=amountOutMin, path=path, to=to, deadline=deadline).buildTransaction({
        'nonce': web3.eth.getTransactionCount(keys["my_account"]),
        'value': web3.toWei(0, 'ether'),
        'gas': keys["gas_limit"],
        'gasPrice':web3.toWei(keys["gas_price"], 'gwei')})
    signed_tx = web3.eth.account.signTransaction(txn, keys["private_key"])
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(web3.toHex(tx_hash))
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("sell successful")
    print("one kif is worth this much eth: " + str(get_price_kif_to_eth()))


def get_price_kif_to_eth():
   
     
    univ2_kif_balance = kif_contract.functions.balanceOf(pair).call()*10**9
    univ2_weth_balance = bnb_contract.functions.balanceOf(pair).call()
    
    return univ2_weth_balance / univ2_kif_balance
    
        
            

def get_price_eth_to_kif():

    
    univ2_kif_balance = kif_contract.functions.balanceOf(pair).call()*10**9
    univ2_weth_balance = bnb_contract.functions.balanceOf(pair).call()

    return univ2_kif_balance / univ2_weth_balance
    
            
        




# lower_bound: the price point to trigger a buy, in terms of kif/eth
# upper_bound: the price point to trigger a sell, in terms of kif/eth
def run(lower_bound, upper_bound, holding=""):
    asset = holding
    

    while True:
        try:
            price = get_price_kif_to_eth()
        except:
            print("Division by zero")
            pass
        print ("price:",price)
        #time.sleep(0.001)
        if price < lower_bound and asset != "kif":
            buy_kif((keys["percentage_of_bnb"]), keys["slippage"], keys["receiver_account"])
            asset = "kif"

            
        elif price > upper_bound and asset != "eth":
            sell_kif(kif_contract.functions.balanceOf(keys["my_account"]).call(), keys["slippage"], keys["receiver_account"])
            asset = "eth"




while True:
     
    time.sleep(0.0001)
    try:
        for event in event_filter.get_new_entries():
            
            xd = Web3.toJSON(event)
            yeni=json.loads(xd)
            token0 = yeni['args']['token0']
            pair = yeni['args']['pair']     
            token1 = yeni['args']['token1']
            print ("token0=", token0)
            print ("token1=", token1)
            print ("pair=", pair)
            #print(time.time())

            if (bnb_token == token0 or bnb_token == token1) and (buy_token == token0 or buy_token == token1):

              
            
                print ("Pair contract found!!", pair)
                print(time.time())
                run(1, 0.6, "eth")

            else:
                print ("Not your token")
    except:

        
        pass


    










