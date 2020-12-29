from lib.same_dl_proof import SameDLProof


class CtSameDLProof():
    def __init__(self, ct1, ct2, w):
        # print('CtSameDLProof')
        self.u = [SameDLProof(ct1u, ct2u, w)
                  for ct1u, ct2u in zip(ct1.u, ct2.u)]
        self.c = SameDLProof(ct1.c, ct2.c, w)

    def to_sol(self):
        u = [uu.to_sol() for uu in self.u]
        c = self.c.to_sol()
        return u, c
