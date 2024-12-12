from pypbc import *

num_U = 5
num_O = 5

params = Parameters(qbits=512, rbits=160)
pairing = Pairing(params)
P = Element.random(pairing, G1)
Q = Element.random(pairing, G1)
e = pairing.apply(P, Q)
r = Element.random(pairing, Zr)

k_i = pairing.apply(P, Q) ** r
sk_U_j = Element.random(pairing, Zr)
pk_U_j = P ** sk_U_j

lambda_O_i = Element.random(pairing, Zr)
TK_1 = k_i * (e ** lambda_O_i)
TK_2 = e ** (lambda_O_i * sk_U_j)


for i in [5, 10, 20, 30, 40]:
    for j in range(1, i):
        sk_U_j_inv = sk_U_j ** -1
        TK_2_inv = (TK_2) ** sk_U_j_inv
        decrypt = TK_1 - TK_2_inv

