from web3 import Web3
import json
import time
from var import keys, contract_keys
from selenium import webdriver
import os
import smtplib
#web3= Web3(Web3.HTTPProvider(infura_url))

web3 = Web3(Web3.IPCProvider())
weth_contract_abi = json.loads(contract_keys["weth_abi"])
weth_contract_address = Web3.toChecksumAddress(contract_keys["weth_token"])
weth_contract = web3.eth.contract(address=weth_contract_address, abi=weth_contract_abi)
kif_contract_abi = json.loads(contract_keys["kif_abi"])
kif_contract_address = Web3.toChecksumAddress(contract_keys["buy_token"])
kif_contract = web3.eth.contract(address=kif_contract_address, abi=kif_contract_abi)

uniswap_contract_abi = json.loads(contract_keys["uniswap_abi"])
uniswap_contract_address = Web3.toChecksumAddress(contract_keys["uniswap_address"])
uniswap_contract = web3.eth.contract(address=uniswap_contract_address, abi=uniswap_contract_abi)

abi=json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
address= Web3.toChecksumAddress("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
etheradress = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
buy_token = Web3.toChecksumAddress (contract_keys["buy_token"])
contract= web3.eth.contract(address=address,abi=abi)

event_filter = contract.events.PairCreated.createFilter(fromBlock="latest")




#print(web3.isConnected())

buy_token = contract_keys["buy_token"]

def buy_kif(eth_out: int, slippage: float, receiver: str, bound, gaz):
    path = [Web3.toChecksumAddress(contract_keys["weth_token"]), Web3.toChecksumAddress(contract_keys["buy_token"])] 
    amountOutMin = int(eth_out * (1/bound) * (1 - slippage))*1000000000000000000
    to = receiver
    deadline = web3.eth.get_block("latest")["timestamp"] + 120 # added 120 seconds from when the transaction was sent
    txn = uniswap_contract.functions.swapExactETHForTokens(amountOutMin=amountOutMin, path=path, to=to, deadline=deadline).buildTransaction({
        'nonce': web3.eth.get_transaction_count(keys["my_account"]),
        'value': web3.toWei(eth_out, 'ether'),
        'gas': keys["gas_limit"],
        'gasPrice':web3.toWei(gaz, 'gwei')})
    signed_tx = web3.eth.account.sign_transaction(txn, keys["private_key"])
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
   
    tx=web3.toHex(tx_hash)
    print(tx)
    driver = webdriver.Chrome("C:\Program Files\Google\Chrome\Application\chromedriver.exe")
    driver.get("https://etherscan.io/tx/{}".format(tx))
    os.system("taskkill /f /im chromedriver.exe")
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("buy successful")
    print("one token is worth this much eth: ", bound)


def sell_kif(kif_out: int, slippage: float, receiver: str):
    amountIn = kif_out
    amountOutMin = int(kif_out * get_price_kif_to_eth() * (1 - slippage))*1000000000000000000
    path = [Web3.toChecksumAddress(contract_keys["buy_token"]), Web3.toChecksumAddress(contract_keys["weth_token"])] 
    to = receiver
    deadline = web3.eth.get_block("latest")["timestamp"] + 120 # added 120 seconds from when the transaction was sent
    txn = uniswap_contract.functions.swapExactTokensForETH(amountIn=amountIn, amountOutMin=amountOutMin, path=path, to=to, deadline=deadline).buildTransaction({
        'nonce': web3.eth.get_transaction_count(keys["my_account"]),
        'value': web3.toWei(0, 'ether'),
        'gas': keys["gas_limit"],
        'gasPrice':web3.toWei(keys["gas_price"], 'gwei')})
    signed_tx = web3.eth.account.sign_transaction(txn, keys["private_key"])
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(web3.toHex(tx_hash))
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print("sell successful")
    print("one kif is worth this much eth: " + str(get_price_kif_to_eth()))



def run(gaz,lower_bound, upper_bound, holding=""):
    asset = holding
    

    
        
    #print (price)
    
        
    
    buy_kif((keys["percentage_of_eth"]), keys["slippage"], keys["receiver_account"],lower_bound,gaz)
    asset = "kif"
    

    #mail()

    pair = listen()


    while True:
        price = get_price_kif_to_eth(pair)
        
        if price > upper_bound and asset != "eth":
            sell_kif(kif_contract.functions.balanceOf(keys["my_account"]).call(), keys["slippage"], keys["receiver_account"])
            asset = "eth"
        
            
def get_price_kif_to_eth(pair):
    univ2_kif_balance = kif_contract.functions.balanceOf(pair).call()
    univ2_weth_balance = weth_contract.functions.balanceOf(pair).call()
    return univ2_weth_balance / univ2_kif_balance
        
            

def listen():
    event_filter = contract.events.PairCreated.createFilter(fromBlock="latest")
    while 1:

        #time.sleep(1) #ddüzelt kullanmadan
        #print("listening")#ddüzelt kullanmadan

        for event in event_filter.get_new_entries():
            
            xd = Web3.toJSON(event)
            yeni=json.loads(xd)
            token0 = yeni['args']['token0']
            pair = yeni['args']['pair']     
            token1 = yeni['args']['token1']
            print ("token0=", token0)
            print ("token1=", token1)
            print ("pair=", pair)
            

            if (buy_token == token0 or buy_token == token1) and (etheradress == token0 or etheradress == token1): 
            
                print ("Pair contract found!!", pair)
                        
                return pair

            else:
                print ("Not your token")

   
def mail():
    sender="alqeren0@gmail.com"
    rec="alqeren1@gmail.com"
    password="aaydin1213"
    message="Token alindi"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, rec, message)







print(web3.net.peerCount)
y="a"
while 1:
    
    #time.sleep(2)
    #e=time.time()
    rt=(web3.geth.txpool.content())
    xq=(Web3.toJSON(rt))
    qer=json.loads(xq)
    mer=qer["pending"].values()

    yer= list(mer)
    #print(yer)
    
    for i in yer:
        wer=list(i.values())
        
        if wer[0]["to"] != None:
            y=Web3.toChecksumAddress(wer[0]["to"])
            

        if y== "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D":

            q=wer[0]["input"]

            #print(q)

            y=q[:74]
            y=y[-40:]
            jo=q[:10]

            #print(y)
            #x=y.replace("0000000000", "")
            #print("Hash:",wer[0]['hash'])
            #print(x)
            #print(jo)
            if jo=="0xf305d719":
                y=Web3.toChecksumAddress(y)
                #print(wer[0]['hash'])
                
                
                #print("Hash:",wer[0]['hash'])
                #print(y)
                
                
                #n=time.time()
                #print(n-e)
                


                if y == Web3.toChecksumAddress(contract_keys['buy_token']):
                    print('Liquidity is sent')
                    print("Hash:",wer[0]['hash'])
                    
                    gaz=int(Web3.toInt(hexstr=wer[0]["gasPrice"])/1000000000)
                    gaz=str(gaz)
                    
                    print("Gas:",gaz)
                    
                    
                    run(gaz,0.00003,0.0022,"eth")
                
            
            

#except:
        #pass
    #if (buy_token == token0 or buy_token == token1) and (etheradress == token0 or etheradress == token1): 
    
     #   print ("Pair contract found!!", pair)
      #  run(0.00165, 0.00331, "eth")        
        

    #else:
     #   print ("Not your token")

        
        
        
        
        
        
        
    








