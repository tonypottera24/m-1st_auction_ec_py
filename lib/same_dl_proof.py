from random import randrange
from web3 import Web3
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256


class SameDLProof():
    def __init__(self, g1, g2, x):
        # print('SameDLProof')
        y1, y2 = g1.scalar(x), g2.scalar(x)
        v = randrange(1, P256.q)
        t1, t2 = g1.scalar(v), g2.scalar(v)
        c = Web3.solidityKeccak(['bytes'], [
            g1.pack() + g2.pack() + y1.pack() + y2.pack() + t1.pack() + t2.pack()])
        c = int.from_bytes(c, byteorder='big') % P256.q
        r = (v + (P256.q - c * x % P256.q)) % P256.q

        assert(t1.equals(g1.scalar(r).add(y1.scalar(c))))
        assert(t2.equals(g2.scalar(r).add(y2.scalar(c))))
        self.t1, self.t2, self.r = t1, t2, r

    def to_sol(self):
        return self.t1.to_sol(), self.t2.to_sol(), self.r
