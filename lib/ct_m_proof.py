from lib.same_dl_proof import SameDLProof
from lib.dl_proof import DLProof
from lib.ec_point import ECPointExt
import random
from web3 import Web3
from fastecdsa.curve import P256


class CtMProof():
    def __init__(self, ctC, y, r, m):
        zm = ECPointExt.z().scalar(m)
        ctC = ctC.sub(zm)
        a = random.randrange(1, P256.q)
        self.ctCA = ctC.scalar(a)
        self.piA = SameDLProof(y, ctC, a)
        self.ya = y.scalar(a)
        self.piR = DLProof(self.ya, r)
        assert(y.scalar(r).equals(ctC))
        assert(self.ya.scalar(r).equals(self.ctCA))

    def to_sol(self):
        return self.ya.to_sol(), self.ctCA.to_sol(), self.piA.to_sol(), self.piR.to_sol()
