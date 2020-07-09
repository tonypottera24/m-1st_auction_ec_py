from random import randrange
from constants.web3 import gas_limit
from lib.dl_proof import DLProof
from lib.same_dl_proof import SameDLProof
from lib.ct_same_dl_proof import CtSameDLProof
from lib.contract_info import ContractInfo
from lib.tx_print import tx_print
from lib.bid_01_proof import Bid01Proof
import time
from lib.ct import Ct
from lib.ec_point import ECPointExt
from fastecdsa import keys, curve


class Auctioneer():
    def __init__(self, index, addr, web3, auction_contract):
        self.index = index
        self.addr = addr
        self.web3 = web3
        self.auction_contract = auction_contract
        self.contract_info = ContractInfo(auction_contract)
        self.contract_info.get_auction_const()
        x, y = keys.gen_keypair(curve.P256)
        self.x, self.y = x, ECPointExt(y)
        print('A{} x = {}'.format(self.index, self.x))
        self.gas = 0

    def phase_1_auctioneer_init(self, value=10):
        pi = DLProof(ECPointExt.g(), self.x).to_sol()
        tx_hash = self.auction_contract.functions.phase1AuctioneerInit(
            self.y.to_sol(), pi).transact({'from': self.addr, 'value': value, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

    def phase_2_time_left(self):
        self.contract_info.get_auction_const()
        t = self.contract_info.timer[1][0] + self.contract_info.timer[1][1]
        # t /= pow(10, 9)
        dt = t - time.time()
        return dt if dt > 0 else 0

    def phase_3_bidder_verification_sum_1(self):
        bid_sums = self.auction_contract.functions.getBidSum().call()
        bid_sum_dec_sols = [Ct.from_sol(bid_sum).decrypt_to_sol(
            self.index, self.x) for bid_sum in bid_sums]
        ux_sols, pi_sols = list(
            map(list, list(zip(*bid_sum_dec_sols))))

        tx_hash = self.auction_contract.functions.phase3BidderVerificationSum1(
            ux_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

    def phase_3_bidder_verification_01_omega(self):
        assert(self.index == 1)
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
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

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
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

    def phase_4_second_highest_bid_decision_omega(self):
        assert(self.index == 1)
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
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

    def phase_4_second_highest_bid_decision_dec(self):
        ctv, ctvv = self.auction_contract.functions.getBidC01ProofJV().call()
        # print('ctv, ctvv = {}, {}'.format(ctv, ctvv))
        uxv_sol, piv_sol = Ct.from_sol(ctv).decrypt_to_sol(self.index, self.x)
        uxvv_sol, pivv_sol = Ct.from_sol(
            ctvv).decrypt_to_sol(self.index, self.x)

        tx_hash = self.auction_contract.functions.phase4SecondHighestBidDecisionDec(
            uxv_sol, piv_sol, uxvv_sol, pivv_sol).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))

    def phase_5_winner_decision(self):
        bid_as = self.auction_contract.functions.getBidA().call()
        bid_a_dec_sols = [Ct.from_sol(bid_a).decrypt_to_sol(
            self.index, self.x) for bid_a in bid_as]
        ux_sols, pi_sols = list(map(list, list(zip(*bid_a_dec_sols))))

        tx_hash = self.auction_contract.functions.phase5WinnerDecision(
            ux_sols, pi_sols).transact({'from': self.addr, 'gas': gas_limit})
        tx_receipt = self.web3.eth.waitForTransactionReceipt(tx_hash)
        self.gas += tx_receipt['gasUsed']
        tx_print(tx_receipt, "A{}".format(self.index))
