from web3 import Web3
import json
import time
from var_p_v2 import keys, contract_keys
import os
import smtplib

#yry = time.time()
#web3 = Web3(Web3.HTTPProvider("https://boterino:alperenrap123@apis.ankr.com/9a36748e41854e0982d87686ee40913f/6dbf6151196c0031013a6be41b9f318c/binance/full/main"))
web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
#web3 = Web3(Web3.WebsocketProvider("wss://boterino:alperenrap123@apis.ankr.com/wss/9a36748e41854e0982d87686ee40913f/6dbf6151196c0031013a6be41b9f318c/binance/full/main"))

print ("Çalışıyor...", web3.eth.getBalance("0xB075076c7A58c9FF84959783e9EB5896aA597a6c")/1000000000000000000)
#mury = time.time()
#print(mury-yry)
address= Web3.toChecksumAddress("0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73")
abi=json.loads('[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[],"name":"INIT_CODE_PAIR_HASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')

buy_token = Web3.toChecksumAddress (contract_keys["buy_token"])
bnb_token = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"

contract= web3.eth.contract(address=address,abi=abi)

###event_filter = contract.events.PairCreated.createFilter(fromBlock="latest")





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


def buy_kif(eth_out: int, slippage: float, receiver: str, bound, gaz):
    path = [Web3.toChecksumAddress(contract_keys["bnb_token"]), Web3.toChecksumAddress(contract_keys["buy_token"])] 
    amountOutMin = int(eth_out * (1/bound) * (1 - slippage))*1000000000000000000
    to = receiver
    deadline = int(time.time()) + 220 # added 120 seconds from when the transaction was sent
    txn = pancakeswap_contract.functions.swapExactETHForTokens(amountOutMin=amountOutMin, path=path, to=to, deadline=deadline).buildTransaction({
        'nonce': web3.eth.getTransactionCount(keys["my_account"]),
        'value': web3.toWei(eth_out, 'ether'),
        'gas': keys["gas_limit"],
        'gasPrice':web3.toWei(gaz, 'gwei')})
    signed_tx = web3.eth.account.signTransaction(txn, keys["private_key"])
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print(web3.toHex(tx_hash))
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print("buy successful")
    
    
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
    #print("one kif is worth this much eth: " + str(get_price_kif_to_eth()))



            




# lower_bound: the price point to trigger a buy, in terms of kif/eth
# upper_bound: the price point to trigger a sell, in terms of kif/eth
def run(gaz,lower_bound, upper_bound, holding=""):
    asset = holding
    

    
        
    #print (price)
    
        
    
    buy_kif((keys["percentage_of_bnb"]), keys["slippage"], keys["receiver_account"],lower_bound,gaz)
    asset = "kif"
    
    while 1:
        aer=kif_contract.functions.balanceOf(keys["my_account"]).call()
        
        if aer != 0:
            print("Şu kadar satın aldın:", aer/10**18)
            break
        else:
            print("Alım başarısız, tekrar deneniyor")
            start() 
   

    mail()

    pair = listen()


    while True:
        price = get_price_kif_to_eth(pair)
        
        if price > upper_bound and asset != "eth":
            sell_kif(kif_contract.functions.balanceOf(keys["my_account"]).call(), keys["slippage"], keys["receiver_account"])
            asset = "eth"
            satmail()


def get_price_kif_to_eth(pair):
    univ2_kif_balance = kif_contract.functions.balanceOf(pair).call()
    univ2_weth_balance = bnb_contract.functions.balanceOf(pair).call()
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
            

            if (buy_token == token0 or buy_token == token1) and (bnb_token == token0 or bnb_token == token1): 
            
                print ("Pair contract found!!", pair)
                        
                return pair

            else:
                print ("Not your token")



def mail():
    sender="pomcashcrypto@gmail.com"
    rec="alqeren1@gmail.com"
    password="umbrellacorp123"
    message="Token alindi 61"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, rec, message)


def satmail():
    sender="pomcashcrypto@gmail.com"
    rec="alqeren1@gmail.com"
    password="umbrellacorp123"
    message="Token satıldı 61"

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, rec, message)

y="a"
#yorki = 0

def start():
    while 1:
        
        #time.sleep(2)
        #e=time.time()
        rt=(web3.geth.txpool.content())
        xq=(Web3.toJSON(rt))
        qer=json.loads(xq)
       
        mer=qer["pending"].values()

        yer= list(mer)
        
        
        for i in yer:
            wer=list(i.values())
            #tr=time.time()
            
            #if yorki != 1:
             #   print(tr-yry)
              #  yorki = 1


            if wer[0]["to"] != None:
                y=Web3.toChecksumAddress(wer[0]["to"])
                

            if y== "0x10ED43C718714eb63d5aA57B78B54704E256024E":

                q=wer[0]["input"]

                

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
                    #print(int(Web3.toInt(hexstr=wer[0]["gasPrice"])/1000000000))
                    
                    
                    #n=time.time()
                    #print(n-yry)
                    #print(n-e)


                    if y == Web3.toChecksumAddress(contract_keys['buy_token']):
                        print('Liquidity is sent')
                        print("Hash:",wer[0]['hash'])
                        
                        gaz=int(Web3.toInt(hexstr=wer[0]["gasPrice"])/1000000000)
                        gaz=str(gaz)
                        
                        print("Gas:",gaz)
                        #print(time.time())
                        
                        run(gaz,0.00026,0.0016,"eth")

start()
