from random import randrange
from web3 import Web3
from fastecdsa.curve import P256


class DLProof():
    def __init__(self, g, x):
        y = g.scalar(x)
        rr = randrange(1, P256.q)
        grr = g.scalar(rr)
        c = Web3.solidityKeccak(['bytes'], [
            g.pack() + y.pack() + grr.pack()])
        c = int.from_bytes(c, byteorder='big') % P256.q
        rrr = (rr + c * x % P256.q) % P256.q
        assert(g.scalar(rrr).equals(grr.add(y.scalar(c))))
        self.grr, self.rrr = grr, rrr

    def to_sol(self):
        return self.grr.to_sol(), self.rrr
