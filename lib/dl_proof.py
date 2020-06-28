from random import randrange
from web3 import Web3
from fastecdsa.curve import P256


class DLProof():
    def __init__(self, g, x):
        y = g.scalar(x)
        v = randrange(1, P256.q)
        t = g.scalar(v)
        c = Web3.solidityKeccak(['bytes'], [
            g.pack() + y.pack() + t.pack()])
        c = int.from_bytes(c, byteorder='big') % P256.q
        r = (v + (P256.q - c * x % P256.q)) % P256.q
        assert(t.equals(g.scalar(r).add(y.scalar(c))))
        self.t, self.r = t, r

    def to_sol(self):
        return self.t.to_sol(), self.r
