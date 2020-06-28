from random import randrange
from lib.ct_same_dl_proof import CtSameDLProof
from fastecdsa import curve, keys


class Bid01Proof():
    def __init__(self, ctu, ctuu):
        # print('Bid01Proof')
        w = keys.gen_private_key(curve.P256)
        self.ctv, self.ctvv = ctu.scalar(w), ctuu.scalar(w)
        self.pi = CtSameDLProof(ctu, ctuu, w)

    def ctv_ctvv_pi_sol(self):
        return self.ctv.to_sol(), self.ctvv.to_sol(), self.pi.to_sol()
