from random import randrange
from lib.same_dl_proof import SameDLProof
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256


class Ct():
    def __init__(self, u, c):
        self.u, self.c = u, c

    @classmethod
    def from_sol(cls, a):
        u = [ECPointExt.from_sol(
            u) if u[0] != 0 and u[1] != 0 else None for u in a[0]]
        c = ECPointExt.from_sol(
            a[1]) if a[1][0] != 0 and a[1][1] != 0 else None
        return cls(u, c)

    @classmethod
    def from_plaintext(cls, m, y):
        r = [randrange(1, P256.q) for yy in y]
        u = [ECPointExt.g().scalar(rr) for rr in r]
        c = m
        for yy, rr in zip(y, r):
            c = c.add(yy.scalar(rr))
        return cls(u, c)

    def decrypt(self, index, x):
        u = self.u[index]
        ux = u.scalar(x)
        pi = SameDLProof(u, ECPointExt.g(), x)
        return ux, pi

    def decrypt_to_sol(self, index, x):
        ux, pi = self.decrypt(index, x)
        return ux.to_sol(), pi.to_sol()

    def scalar(self, k):
        u = [uu.scalar(k) for uu in self.u]
        c = self.c.scalar(k)
        return Ct(u, c)

    def to_sol(self):
        u = [uu.to_sol() for uu in self.u]
        c = self.c.to_sol()
        return u, c
