from fastecdsa.curve import P256
from fastecdsa.point import Point


class ECPointExt():
    def __init__(self, pt):
        self.pt = pt

    @classmethod
    def zero(cls):
        return cls(Point.IDENTITY_ELEMENT)

    @classmethod
    def g(cls):
        return cls(P256.G)

    @classmethod
    def z(cls):
        return cls(P256.G * 2)

    @classmethod
    def from_sol(cls, a):
        return cls(Point(a[0], a[1], curve=P256))

    def to_sol(self):
        return self.pt.x, self.pt.y

    def equals(self, pt):
        return self.pt.x % P256.p == pt.pt.x % P256.p and self.pt.y % P256.p == pt.pt.y % P256.p

    def pack(self):
        return self.pt.x.to_bytes(32, byteorder='big') + self.pt.y.to_bytes(32, byteorder='big')

    def add(self, pt):
        return ECPointExt(self.pt + pt.pt)

    def sub(self, pt):
        return ECPointExt(self.pt - pt.pt)

    def scalar(self, k):
        return ECPointExt(self.pt * k)
