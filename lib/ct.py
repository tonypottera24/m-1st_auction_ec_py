from lib.big_number import BigNumber
from random import randrange
from lib.same_dl_proof import SameDLProof


class Ct():
    def __init__(self, u1, u2, c):
        self.u1, self.u2, self.c = u1, u2, c

    @classmethod
    def from_sol(cls, a):
        return cls(BigNumber.from_sol(a[0]).to_py(), BigNumber.from_sol(a[1]).to_py(), BigNumber.from_sol(a[2]).to_py())

    @classmethod
    def from_plaintext(cls, m, y1, y2, p, q, g):
        m %= p
        r1, r2 = randrange(1, q), randrange(1, q)
        u1, u2 = pow(g, r1, p), pow(g, r2, p)
        c = (((m * pow(y1, r1, p)) % p) * pow(y2, r2, p)) % p
        return cls(u1, u2, c)

    def decrypt(self, index, x, p, q, g):
        u = self.u1 if index == 0 else self.u2
        assert(0 < u and u < p)
        assert(0 < x and x < q)
        ux = pow(u, x, p)
        ux_inv = pow(ux, -1, p)
        assert(ux * ux_inv % p == 1)
        pi = SameDLProof(u, g, x, p, q)
        return ux, ux_inv, pi

    def decrypt_to_sol(self, index, x, p, q, g):
        ux, ux_inv, pi = self.decrypt(index, x, p, q, g)
        return BigNumber.from_py(ux).to_sol(), BigNumber.from_py(ux_inv).to_sol(), pi.to_sol()

    def mul_z(self, z, p):
        assert(z > 0)
        return Ct(self.u1, self.u2, self.c * z % p)

    def pow(self, k, p):
        assert(k > 0)
        return Ct(pow(self.u1, k, p), pow(self.u2, k, p), pow(self.c, k, p))

    def to_sol(self):
        if self.u1 == 0:
            print('u1 == 0!!!')
        if self.u2 == 0:
            print('u2 == 0!!!')
        if self.c == 0:
            print('c == 0!!!')
        return BigNumber.from_py(self.u1).to_sol(), BigNumber.from_py(self.u2).to_sol(), BigNumber.from_py(self.c).to_sol()
