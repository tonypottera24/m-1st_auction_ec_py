from random import randrange
from lib.ct_same_dl_proof import CtSameDLProof


class Bid01Proof():
    def __init__(self, ctu, ctuu, p, q):
        w = randrange(1, q)
        self.ctv, self.ctvv = ctu.pow(w, p), ctuu.pow(w, p)
        self.pi = CtSameDLProof(ctu, ctuu, w, p, q)

    def ctv_ctvv_pi_sol(self):
        return self.ctv.to_sol(), self.ctvv.to_sol(), self.pi.to_sol()
