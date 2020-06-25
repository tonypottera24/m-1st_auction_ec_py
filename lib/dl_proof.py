from random import randrange
from web3 import Web3
from lib.big_number import BigNumber


class DLProof():
    def __init__(self, g, x, p, q):
        y = pow(g, x, p)
        v = randrange(1, q)
        t = pow(g, v, p)
        c = Web3.solidityKeccak(['bytes'], [
            BigNumber.from_py(g).val + BigNumber.from_py(y).val + BigNumber.from_py(t).val])
        c = int.from_bytes(c, byteorder='big') % q
        r = (v - (c * x) % q) % q
        if r < 0:
            r += q
        assert(t == (pow(g, r, p) * pow(y, c, p)) % p)
        self.t, self.r = t, r

    def to_sol(self):
        return BigNumber.from_py(self.t).to_sol(), BigNumber.from_py(self.r).to_sol()
