from random import randrange
from lib.same_dl_proof import SameDLProof
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256


class Ct():
    def __init__(self, u1, u2, c):
        self.u1, self.u2, self.c = u1, u2, c

    @classmethod
    def from_sol(cls, a):
        u1 = ECPointExt.from_sol(
            a[0]) if a[0][0] != 0 and a[0][1] != 0 else None
        u2 = ECPointExt.from_sol(
            a[1]) if a[1][0] != 0 and a[1][1] != 0 else None
        c = ECPointExt.from_sol(
            a[2]) if a[2][0] != 0 and a[2][1] != 0 else None
        return cls(u1, u2, c)

    @classmethod
    def from_plaintext(cls, m, y1, y2):
        r1, r2 = randrange(1, P256.q), randrange(1, P256.q)
        u1, u2 = ECPointExt.g().scalar(r1), ECPointExt.g().scalar(r2)
        c = m.add(y1.scalar(r1)).add(y2.scalar(r2))
        return cls(u1, u2, c)

    def decrypt(self, index, x):
        u = self.u1 if index == 0 else self.u2
        ux = u.scalar(x)
        pi = SameDLProof(u, ECPointExt.g(), x)
        return ux, pi

    def decrypt_to_sol(self, index, x):
        ux, pi = self.decrypt(index, x)
        return ux.to_sol(), pi.to_sol()

    def scalar(self, k):
        return Ct(self.u1.scalar(k), self.u2.scalar(k), self.c.scalar(k))

    def to_sol(self):
        return self.u1.to_sol(), self.u2.to_sol(), self.c.to_sol()
