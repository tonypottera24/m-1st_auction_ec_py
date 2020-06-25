from web3 import Web3


class BigNumber():
    def __init__(self, val, neg, bitlen):
        self.val, self.neg, self.bitlen = val, neg, bitlen

    @classmethod
    def from_py(cls, a):
        val = Web3.toBytes(a)
        if len(val) < 32:
            val = bytes(32 - len(val)) + val
        assert(len(val) >= 32)
        return cls(val, a < 0, a.bit_length())

    @classmethod
    def from_sol(cls, a):
        return cls(a[0], a[1], a[2])

    def to_py(self):
        return Web3.toInt(self.val) if self.neg == False else - Web3.toInt(self.val)

    def to_sol(self):
        return self.val, self.neg, self.bitlen
