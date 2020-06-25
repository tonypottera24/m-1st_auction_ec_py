from lib.contract_info import ContractInfo
from lib.ct import Ct
from constants.web3 import gas_limit
from lib.tx_print import tx_print
from lib.big_number import BigNumber


class Bidder():
    def __init__(self, index, addr, web3, auction_contract):
        self.web3 = web3
        self.auction_contract = auction_contract
        self.index = index
        self.addr = addr
        self.contract_info = ContractInfo(auction_contract)
        self.p = BigNumber.from_sol(
            self.auction_contract.functions.p().call()).to_py()
        self.q = BigNumber.from_sol(
            self.auction_contract.functions.q().call()).to_py()
        self.g = BigNumber.from_sol(
            self.auction_contract.functions.g().call()).to_py()
        self.z = BigNumber.from_sol(
            self.auction_contract.functions.z().call()).to_py()
        self.contract_info.get_auction_const()

    def phase_2_bidder_join(self, bid_price_j, value=10):
        self.bid_price_j = bid_price_j
        y1, y2 = self.auction_contract.functions.getElgamalY().call()
        y1 = BigNumber.from_sol(y1).to_py()
        y2 = BigNumber.from_sol(y2).to_py()
        bid = []
        for j in range(len(self.contract_info.price)):
            zt = pow(self.z, 1 if j == bid_price_j else 0, self.p)
            ct = Ct.from_plaintext(zt, y1, y2, self.p, self.q, self.g)
            bid.append(ct.to_sol())
        tx_hash = self.auction_contract.functions.phase2BidderJoin(bid).transact(
            {'from': self.addr, 'value': value, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_print(tx_receipt, "B{} bid_price_j = {}".format(
            self.index, bid_price_j))

    def phase_6_payment(self):
        secondHighestBidPriceJ = self.auction_contract.functions.secondHighestBidPriceJ().call()
        price = self.contract_info.price[secondHighestBidPriceJ]
        tx_hash = self.auction_contract.functions.phase6Payment().transact(
            {'from': self.addr, 'value': price, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_print(tx_receipt, "B{} payed = {}".format(
            self.index, price))