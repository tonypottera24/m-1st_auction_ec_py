from random import randrange
from constants.web3 import gas_limit
from lib.dl_proof import DLProof
from lib.same_dl_proof import SameDLProof
from lib.ct_same_dl_proof import CtSameDLProof
from lib.contract_info import AuctionInfo
from lib.tx_print import tx_print
from lib.bid_01_proof import Bid01Proof
import time
from lib.ct import Ct
from lib.ec_point import ECPointExt
from fastecdsa import keys, curve


class Bidder():
    def __init__(self, index, addr, web3, auction_contract):
        self.index = index
        self.addr = addr
        self.web3 = web3
        self.auction_contract = auction_contract
        self.auction_info = AuctionInfo(auction_contract)
        x, y = keys.gen_keypair(curve.P256)
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
        self.auction_info.update()
        t = self.auction_info.timer[0][0] + self.auction_info.timer[0][1]
        # t /= pow(10, 9)
        dt = t - time.time()
        return dt if dt > 0 else 0

    def phase_2_bidder_submit_bid(self, bid_price_j, value=10):
        self.bid_price_j = bid_price_j
        y = self.auction_contract.functions.getElgamalY().call()
        y = [ECPointExt.from_sol(yy) for yy in y]
        bid = []
        for j in range(len(self.auction_info.price)):
            zt = ECPointExt.z().scalar(1 if j == bid_price_j else 0)
            ct = Ct.from_plaintext(zt, y)
            bid.append(ct.to_sol())
        tx_hash = self.auction_contract.functions.phase2BidderSubmitBid(bid).transact(
            {'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{} bid_price_j = {}".format(
            self.index, bid_price_j))

    def phase_3_bidder_verification_sum_1(self):
        bid_sums = self.auction_contract.functions.getBidSum().call()
        bid_sum_dec_sols = [Ct.from_sol(bid_sum).decrypt_to_sol(
            self.index, self.x) for bid_sum in bid_sums]
        ux_sols, pi_sols = list(
            map(list, list(zip(*bid_sum_dec_sols))))

        tx_hash = self.auction_contract.functions.phase3BidderVerificationSum1(
            ux_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_3_bidder_verification_01_omega(self):
        assert(self.index == 0)
        b_list_length = self.auction_contract.functions.getBListLength().call()
        # print('b_list_length = {}'.format(b_list_length))
        ctv_solss, ctvv_solss, pi_solss = [], [], []
        for i in range(b_list_length):
            # print('i = {}'.format(i))
            ctus, ctuus = self.auction_contract.functions.getBidderBid01ProofU(
                i).call()
            ctus = [Ct.from_sol(ctu) for ctu in ctus]
            ctuus = [Ct.from_sol(ctuu) for ctuu in ctuus]
            bid_01_proof_sols = [Bid01Proof(
                ctu, ctuu).ctv_ctvv_pi_sol() for ctu, ctuu in zip(ctus, ctuus)]
            ctv_sols, ctvv_sols, pi_sols = list(
                map(list, list(zip(*bid_01_proof_sols))))
            ctv_solss.append(ctv_sols)
            ctvv_solss.append(ctvv_sols)
            pi_solss.append(pi_sols)
        tx_hash = self.auction_contract.functions.phase3BidderVerification01Omega(
            ctv_solss, ctvv_solss, pi_solss).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_3_bidder_verification_01_dec(self):
        b_list_length = self.auction_contract.functions.getBListLength().call()
        ctvs, ctvvs = [], []
        uxv_solss, piv_solss = [], []
        uxvv_solss, pivv_solss = [], []
        for i in range(b_list_length):
            ctvs, ctvvs = self.auction_contract.functions.getBidderBid01ProofV(
                i).call()
            ctv_dec_sols = [Ct.from_sol(ctv).decrypt_to_sol(
                self.index, self.x) for ctv in ctvs]
            ctvv_dec_sols = [Ct.from_sol(ctvv).decrypt_to_sol(
                self.index, self.x) for ctvv in ctvvs]
            uxv_sols, piv_sols = list(
                map(list, list(zip(*ctv_dec_sols))))
            uxvv_sols, pivv_sols = list(
                map(list, list(zip(*ctvv_dec_sols))))
            uxv_solss.append(uxv_sols)
            piv_solss.append(piv_sols)
            uxvv_solss.append(uxvv_sols)
            pivv_solss.append(pivv_sols)
        tx_hash = self.auction_contract.functions.phase3BidderVerification01Dec(
            uxv_solss, piv_solss, uxvv_solss, pivv_solss).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_4_second_highest_bid_decision_omega(self):
        assert(self.index == 0)
        ctus, ctuus = self.auction_contract.functions.getBidC01ProofU().call()
        # print('ctus, ctuus = {}, {}'.format(ctus, ctuus))
        ctus = [Ct.from_sol(ctu) for ctu in ctus]
        ctuus = [Ct.from_sol(ctuu) for ctuu in ctuus]
        bid_01_proof_sols = [Bid01Proof(
            ctu, ctuu).ctv_ctvv_pi_sol() for ctu, ctuu in zip(ctus, ctuus)]
        ctv_sols, ctvv_sols, pi_sols = list(
            map(list, list(zip(*bid_01_proof_sols))))

        tx_hash = self.auction_contract.functions.phase4SecondHighestBidDecisionOmega(
            ctv_sols, ctvv_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_4_second_highest_bid_decision_dec(self):
        ctv, ctvv = self.auction_contract.functions.getBidC01ProofJV().call()
        # print('ctv, ctvv = {}, {}'.format(ctv, ctvv))
        uxv_sol, piv_sol = Ct.from_sol(ctv).decrypt_to_sol(self.index, self.x)
        uxvv_sol, pivv_sol = Ct.from_sol(
            ctvv).decrypt_to_sol(self.index, self.x)

        tx_hash = self.auction_contract.functions.phase4SecondHighestBidDecisionDec(
            uxv_sol, piv_sol, uxvv_sol, pivv_sol).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_5_winner_decision(self):
        bid_as = self.auction_contract.functions.getBidA().call()
        bid_a_dec_sols = [Ct.from_sol(bid_a).decrypt_to_sol(
            self.index, self.x) for bid_a in bid_as]
        ux_sols, pi_sols = list(map(list, list(zip(*bid_a_dec_sols))))

        tx_hash = self.auction_contract.functions.phase5WinnerDecision(
            ux_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{}".format(self.index))

    def phase_6_payment(self):
        secondHighestBidPriceJ = self.auction_contract.functions.secondHighestBidPriceJ().call()
        price = self.auction_info.price[secondHighestBidPriceJ]
        tx_hash = self.auction_contract.functions.phase6Payment().transact(
            {'from': self.addr, 'value': price, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gasUsed += tx_receipt['gasUsed']
        tx_print(tx_receipt, "B{} payed = {}".format(
            self.index, price))
