from lib.same_dl_proof import SameDLProof


class CtSameDLProof():
    def __init__(self, ct1, ct2, w):
        # print('CtSameDLProof')
        self.u1 = SameDLProof(ct1.u1, ct2.u1, w)
        self.u2 = SameDLProof(ct1.u2, ct2.u2, w)
        self.c = SameDLProof(ct1.c, ct2.c, w)

    def to_sol(self):
        return self.u1.to_sol(), self.u2.to_sol(), self.c.to_sol()
