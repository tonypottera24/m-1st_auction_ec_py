from lib.big_number import BigNumber
from lib.ct import Ct
from web3 import Web3
from constants.crypto import p, q, g, z
from constants.auction import price, time_limit


class ContractInfo():
    def __init__(self, auction_contract):
        self.auction_contract = auction_contract

    def get_auction_const(self):
        self.price = self.auction_contract.functions.getPrice().call()
        for i in range(len(self.price)):
            assert(self.price[i] == price[i])
        self.timer = self.auction_contract.functions.getTimer().call()
        for i in range(len(self.timer)):
            assert(self.timer[i][1] == time_limit[i])
