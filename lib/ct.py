from lib.ct_01_proof import Ct01Proof
from random import randrange
from lib.same_dl_proof import SameDLProof
from lib.ec_point import ECPointExt
from fastecdsa.curve import P256
import functools


class Ct():
    def __init__(self, u, c, r=None, ct_01_proof=None):
        self.u, self.c = u, c
        self.r = r
        self.ct_01_proof = ct_01_proof

    @classmethod
    def from_sol(cls, a: list):
        u = ECPointExt.from_sol(
            a[0]) if a[0][0] != 0 and a[0][1] != 0 else None
        c = ECPointExt.from_sol(
            a[1]) if a[1][0] != 0 and a[1][1] != 0 else None
        return cls(u, c)

    @classmethod
    def from_vote(cls, v: bool, y: ECPointExt):
        r = randrange(1, P256.q)
        u = ECPointExt.g().scalar(r)
        zt = ECPointExt.z().scalar(1 if v else 0)
        c = zt.add(y.scalar(r))
        return cls(u, c, r, ct_01_proof=Ct01Proof(v, u, c, r, y))

    def scalar(self, k: int):
        u = self.u.scalar(k)
        c = self.c.scalar(k)
        return Ct(u, c, r=self.r + k % P256.q if self.r != None else None)

    def add(self, ct):
        return Ct(self.u.add(ct.u), self.c.add(ct.c), r=(self.r + ct.r) % P256.q)

    def decrypt(self, x: int):
        ux = self.u.scalar(x)
        pi = SameDLProof(self.u, ECPointExt.g(), x)
        return ux, pi

    def decrypt_to_sol(self, x: int):
        ux, pi = self.decrypt(x)
        return ux.to_sol(), pi.to_sol()

    def to_sol(self):
        return self.u.to_sol(), self.c.to_sol()

    def to_sol_with_01_proof(self):
        return self.to_sol(), self.ct_01_proof.to_sol()
