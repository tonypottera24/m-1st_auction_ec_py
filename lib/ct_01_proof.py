from lib.ec_point import ECPointExt
import random
from web3 import Web3
from fastecdsa.curve import P256


class Ct01Proof():
    def __init__(self, v: bool, a, b, r: int, y: ECPointExt):
        n = pow(2, 256)
        if v == False:
            # 1. Simulate the v = 1 proof.
            c1 = random.randrange(0, n)
            rrr1 = random.randrange(1, P256.q)

            bb = b.sub(ECPointExt.z())
            aa1 = ECPointExt.g().scalar(rrr1).sub(a.scalar(c1))
            bb1 = y.scalar(rrr1).sub(bb.scalar(c1))

            # 2. Setup the v = 0 proof.
            rr0 = random.randrange(1, P256.q)
            aa0 = ECPointExt.g().scalar(rr0)
            bb0 = y.scalar(rr0)

            # 3. Create the challenge for v = 0 proof.
            c = Web3.solidityKeccak(['bytes'], [
                y.pack() + a.pack() + b.pack() + aa0.pack() + bb0.pack() + aa1.pack() + bb1.pack()])
            c = int.from_bytes(c, byteorder='big') % n
            c0 = (c - c1) % n

            # 4. Compute the v = 0 proof.
            rrr0 = (rr0 + c0 * r % P256.q) % P256.q

        else:  # v == 1
            # 1. Simulate the v = 0 proof.
            c0 = random.randrange(0, n)
            rrr0 = random.randrange(1, P256.q)

            aa0 = ECPointExt.g().scalar(rrr0).sub(a.scalar(c0))
            bb0 = y.scalar(rrr0).sub(b.scalar(c0))

            # 2. Setup the v = 1 proof.
            rr1 = random.randrange(1, P256.q)
            aa1 = ECPointExt.g().scalar(rr1)
            bb1 = y.scalar(rr1)

            # 3. Create the challenge for v = 1 proof.
            c = Web3.solidityKeccak(['bytes'], [
                y.pack() + a.pack() + b.pack() + aa0.pack() + bb0.pack() + aa1.pack() + bb1.pack()])
            c = int.from_bytes(c, byteorder='big') % n
            c1 = (c - c0) % n

            # 4. Compute the v = 0 proof.
            rrr1 = (rr1 + c1 * r % P256.q) % P256.q

        # 5. proof \pi
        self.aa0, self.aa1 = aa0, aa1
        self.bb0, self.bb1 = bb0, bb1
        self.c0, self.c1 = c0, c1
        self.rrr0, self.rrr1 = rrr0, rrr1

        assert(ECPointExt.g().scalar(rrr0).equals(aa0.add(a.scalar(c0))))
        assert(ECPointExt.g().scalar(rrr1).equals(aa1.add(a.scalar(c1))))
        assert(y.scalar(rrr0).equals(bb0.add(b.scalar(c0))))
        assert(y.scalar(rrr1).equals(bb1.add(b.sub(ECPointExt.z()).scalar(c1))))
        c = Web3.solidityKeccak(['bytes'], [y.pack(
        ) + a.pack() + b.pack() + aa0.pack() + bb0.pack() + aa1.pack() + bb1.pack()])
        c = int.from_bytes(c, byteorder='big') % n
        assert((c0 + c1) % n == c % n)

    def to_sol(self):
        return self.aa0.to_sol(), self.aa1.to_sol(), self.bb0.to_sol(), self.bb1.to_sol(), self.c0, self.c1, self.rrr0, self.rrr1
