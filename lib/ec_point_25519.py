from constants.crypto import p, q, d, Gx, Gy


class ECPointExt():
    def __init__(self, x, y, z, t):
        self.x, self.y, self.z, self.t = x % p, y % p, z % p, t % p

    @classmethod
    def zero(cls):
        return cls(0, 1, 1, 0)

    @classmethod
    def g(cls):
        return cls(Gx, Gy, 1, Gx * Gy % p)

    @classmethod
    def z(cls):
        return cls.g().scalar(2)

    @classmethod
    def from_sol(cls, a):
        return cls(a[0], a[1], a[2], a[3])

    def to_sol(self):
        return self.x, self.y, self.z, self.t

    def equals(self, pt):
        return self.x * pow(self.z, -1, p) % p == pt.x * pow(pt.z, -1, p) % p and self.y * pow(self.z, -1, p) % p == pt.y * pow(pt.z, -1, p) % p

    def pack(self):
        return self.x.to_bytes(32, byteorder='big') + self.y.to_bytes(32, byteorder='big') + self.z.to_bytes(32, byteorder='big') + self.t.to_bytes(32, byteorder='big')

    # def neg(self):
    #     return self.scalar(q - 1)

    def add(self, pt):
        # add-2008-hwcd, strongly unified.
        X1, Y1, Z1, T1 = self.x % p, self.y % p, self.z % p, self.t % p
        X2, Y2, Z2, T2 = pt.x % p, pt.y % p, pt.z % p, pt.t % p
        A = X1 * X2 % p
        B = Y1 * Y2 % p
        C = (T1 * d % p) * T2 % p
        D = Z1 * Z2 % p
        E = (((X1 + Y1 % p) * (X2 + Y2 % p) % p + (p - A)) % p + (p - B)) % p
        F = (D + (p - C)) % p
        G = (D + C) % p
        H = (B + A) % p
        X3 = E * F % p
        Y3 = G * H % p
        T3 = E * H % p
        Z3 = F * G % p
        return ECPointExt(X3, Y3, Z3, T3)

    # def sub(self, pt1, pt2):
    #     return add(pt1, neg(pt2))

    def double(self):
        # dbl-2008-hwcd
        X1, Y1, Z1, T1 = self.x % p, self.y % p, self.z % p, self.t % p
        A = X1 * X1 % p
        B = Y1 * Y1 % p
        C = 2 * (Z1 * Z1 % p) % p
        D = p - A
        e = (X1 + Y1) % p
        E = ((e * e % p + (p - A)) % p + (p - B)) % p
        G = (D + B) % p
        F = (G + (p - C)) % p
        H = (D + (p - B)) % p
        X3 = E * F % p
        Y3 = G * H % p
        T3 = E * H % p
        Z3 = F * G % p
        return ECPointExt(X3, Y3, Z3, T3)

    def scalar(self, k):
        k %= q
        result = self.zero()
        while k > 0:
            if (k & 1 == 1):
                result = result.add(self)
            self = self.double()
            k >>= 1
        return result
