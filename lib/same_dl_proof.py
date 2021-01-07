from random import randrange
from web3 import Web3
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256


class SameDLProof():
    def __init__(self, g1, g2, x):
        # print('SameDLProof')
        y1, y2 = g1.scalar(x), g2.scalar(x)
        rr = randrange(1, P256.q)
        grr1, grr2 = g1.scalar(rr), g2.scalar(rr)
        c = Web3.solidityKeccak(['bytes'], [
            g1.pack() + g2.pack() + y1.pack() + y2.pack() + grr1.pack() + grr2.pack()])
        c = int.from_bytes(c, byteorder='big') % P256.q
        rrr = (rr + c * x % P256.q) % P256.q

        assert(g1.scalar(rrr).equals(grr1.add(y1.scalar(c))))
        assert(g2.scalar(rrr).equals(grr2.add(y2.scalar(c))))
        self.grr1, self.grr2, self.rrr = grr1, grr2, rrr

    def to_sol(self):
        return self.grr1.to_sol(), self.grr2.to_sol(), self.rrr
