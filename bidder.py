from lib.ct_m_proof import CtMProof
from random import randrange
from constants.web3 import gas_limit
from lib.dl_proof import DLProof
from lib.same_dl_proof import SameDLProof
from lib.tx_print import tx_print
import time
from lib.ct import Ct
from lib.ec_point import ECPointExt
from fastecdsa import keys
import functools
from fastecdsa.curve import P256


class Bidder():
    def __init__(self, index, addr, web3, auction_contract):
        self.index = index
        self.addr = addr
        self.web3 = web3
        self.auction_contract = auction_contract
        x, y = keys.gen_keypair(P256)
        self.x, self.y = x, ECPointExt(y)
        print('B{} x = {}'.format(self.index, self.x))
        self.gasUsed = 0

    def phase_1_bidder_init(self, value=10):
        pi = DLProof(ECPointExt.g(), self.x).to_sol()
        tx_hash = self.auction_contract.functions.phase1BidderInit(
            self.y.to_sol(), pi).transact({'from': self.addr, 'value': value, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_1_time_left(self):
        t0 = self.auction_contract.functions.timer(0).call()
        t = t0[0] + t0[1]
        dt = t - time.time()
        return dt if dt > 0 else 0

    def phase_2_bidder_submit_bid(self, bid_price_j, value=10):
        self.bid_price_j = bid_price_j
        y = ECPointExt.from_sol(
            self.auction_contract.functions.elgamalY().call())
        price_length = self.auction_contract.functions.priceLength().call()

        self.bids = []
        for j in range(price_length):
            self.bids.append(Ct.from_vote(j == bid_price_j, y))
        bid_pi01_sols = [bid.to_sol_with_01_proof() for bid in self.bids]
        bid, pi01 = list(
            map(list, list(zip(*bid_pi01_sols))))
        bidSum = functools.reduce(lambda ct1, ct2: ct1.add(ct2), self.bids)
        piM = CtMProof(bidSum.c, y, bidSum.r, 1).to_sol()

        tx_hash = self.auction_contract.functions.phase2BidderSubmitBid(bid, pi01, piM).transact(
            {'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{} bid_price_j = {}".format(
            self.index, bid_price_j))

    def phase_3_m_1st_price_decision_prepare(self):
        price_length = self.auction_contract.functions.priceLength().call()
        bidCs = [Ct.from_sol(self.auction_contract.functions.bidC(
            i).call()) for i in range(price_length)]
        a = randrange(1, P256.q)
        pi_sols = [SameDLProof(bidC.u, bidC.c, a).to_sol() for bidC in bidCs]
        ctA_sols = [bidC.scalar(a).to_sol() for bidC in bidCs]

        tx_hash = self.auction_contract.functions.phase3M1stPriceDecisionPrepare(
            ctA_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_4_m_1st_price_decision(self):
        jM = self.auction_contract.functions.jM().call()
        ct = Ct.from_sol(self.auction_contract.functions.bidCA(jM).call())

        ux, pi = ct.decrypt_to_sol(self.x)

        tx_hash = self.auction_contract.functions.phase4M1stPriceDecision(ux,
                                                                          pi).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_5_winner_decision(self):
        y = ECPointExt.from_sol(
            self.auction_contract.functions.elgamalY().call())
        jM = self.auction_contract.functions.jM().call()
        bidA = [self.bids[-1]]
        for i in reversed(range(len(self.bids) - 1)):
            bidA = [self.bids[i].add(bidA[0])] + bidA

        piM_sols = CtMProof(bidA[jM].c, y, bidA[jM].r, 1).to_sol()

        tx_hash = self.auction_contract.functions.phase5WinnerDecision(
            piM_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_6_payment(self):
        jM = self.auction_contract.functions.jM().call()
        price = self.auction_contract.functions.price(jM-1).call()
        tx_hash = self.auction_contract.functions.phase6Payment().transact(
            {'from': self.addr, 'value': price, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{} payed = {}".format(
            self.index, price))
