from lib.same_dl_proof import SameDLProof


class CtSameDLProof():
    def __init__(self, ct1, ct2, w):
        # print('CtSameDLProof')
        self.u = SameDLProof(ct1.u, ct2.u, w)
        self.c = SameDLProof(ct1.c, ct2.c, w)

    def to_sol(self):
        return self.u.to_sol(), self.c.to_sol()
