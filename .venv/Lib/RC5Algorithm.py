import struct

class RC5Algorithm:

    def __init__(self, key_length=2040, rounds=12, key=b''):
        self.w = 32
        self.r = rounds
        self.key = key
        self.b = len(key)
        self.s = self.expand_key()

    def expand_key(self):
        P = 0xB7E15163
        Q = 0x9E3779B9

        n = 2 * (self.r + 1)
        s = [0] * n
        key = list(self.key) + [0] * (n - self.b)

        s[0] = P
        for i in range(1, n):
            s[i] = (s[i - 1] + Q) & 0xFFFFFFFF

        j = 0
        A = 0
        B = 0
        for i in range(3 * max(n, self.b)):
            A = s[i % n] = ((s[i % n] + A + B) & 0xFFFFFFFF)
            B = (key[j] + A) & 0xFFFFFFFF
            j = (j + 1) % self.b

        return s

    def encrypt_block(self, data):
        A, B = struct.unpack('<II', data)
        A = (A + self.s[0]) & 0xFFFFFFFF
        B = (B + self.s[1]) & 0xFFFFFFFF

        for i in range(1, self.r + 1):
            A = (A ^ B) & 0xFFFFFFFF
            A = (A << (B % 32) | A >> (32 - (B % 32))) & 0xFFFFFFFF
            A = (A + self.s[2 * i]) & 0xFFFFFFFF

            B = (B ^ A) & 0xFFFFFFFF
            B = (B << (A % 32) | B >> (32 - (A % 32))) & 0xFFFFFFFF
            B = (B + self.s[2 * i + 1]) & 0xFFFFFFFF

        return struct.pack('<II', A, B)

    def decrypt_block(self, data):
        A, B = struct.unpack('<II', data)

        for i in range(self.r, 0, -1):
            B = (B - self.s[2 * i + 1]) & 0xFFFFFFFF
            B = (B >> (A % 32) | B << (32 - (A % 32))) & 0xFFFFFFFF
            B = (B ^ A) & 0xFFFFFFFF

            A = (A - self.s[2 * i]) & 0xFFFFFFFF
            A = (A >> (B % 32) | A << (32 - (B % 32))) & 0xFFFFFFFF
            A = (A ^ B) & 0xFFFFFFFF

        B = (B - self.s[1]) & 0xFFFFFFFF
        A = (A - self.s[0]) & 0xFFFFFFFF

        return struct.pack('<II', A, B)

