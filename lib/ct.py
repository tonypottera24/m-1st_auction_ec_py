from random import randrange
from lib.same_dl_proof import SameDLProof
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256


class Ct():
    def __init__(self, u, c):
        self.u, self.c = u, c

    @classmethod
    def from_sol(cls, a: list):
        u = ECPointExt.from_sol(
            a[0]) if a[0][0] != 0 and a[0][1] != 0 else None
        c = ECPointExt.from_sol(
            a[1]) if a[1][0] != 0 and a[1][1] != 0 else None
        return cls(u, c)

    @classmethod
    def from_plaintext(cls, m: ECPointExt, y: ECPointExt):
        r = randrange(1, P256.q)
        u = ECPointExt.g().scalar(r)
        c = m
        for yy in y:
            c = c.add(yy.scalar(r))
        return cls(u, c)

    def scalar(self, k: int):
        u = self.u.scalar(k)
        c = self.c.scalar(k)
        return Ct(u, c)

    def decrypt(self, x: int):
        ux = self.u.scalar(x)
        pi = SameDLProof(self.u, ECPointExt.g(), x)
        return ux, pi

    def decrypt_to_sol(self, x: int):
        ux, pi = self.decrypt(x)
        return ux.to_sol(), pi.to_sol()

    def to_sol(self):
        return self.u.to_sol(), self.c.to_sol()
