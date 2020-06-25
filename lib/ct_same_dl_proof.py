from lib.same_dl_proof import SameDLProof
from lib.big_number import BigNumber


class CtSameDLProof():
    def __init__(self, ct1, ct2, w, p, q):
        self.u1 = SameDLProof(ct1.u1, ct2.u1, w, p, q)
        self.u2 = SameDLProof(ct1.u2, ct2.u2, w, p, q)
        self.c = SameDLProof(ct1.c, ct2.c, w, p, q)

    def to_sol(self):
        return self.u1.to_sol(), self.u2.to_sol(), self.c.to_sol()
