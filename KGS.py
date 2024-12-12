import numpy as np
from pypbc import *


class KGS:
    def GenKey(self, DO_num, SU_num, feature_vector_dimension, K_A):
        # 生成双线性对参数
        params = Parameters(qbits=512, rbits=160)
        pairing = Pairing(params)
        P = Element.random(pairing, G1)
        Q = Element.random(pairing, G1)
        e = pairing.apply(P, Q)

        # 生成矩阵M和它的逆
        M = np.random.randint(
            1, 100, size=(2 * feature_vector_dimension, 2 * feature_vector_dimension)
        )
        M_inv = np.linalg.pinv(M)

        # 生成sk_U_j、pk_U_j、M_U_j和M_U_j一撇
        sk_U = []
        pk_U = []
        M_U = []
        M_U_pie = []
        for j in range(SU_num):
            sk_U_j = Element.random(pairing, Zr)
            sk_U.append(sk_U_j)
            pk_U.append(P ** sk_U_j)
            M_U_j_pie = np.random.rand(
                2 * feature_vector_dimension, 2 * feature_vector_dimension
            )
            M_U_pie.append(M_U_j_pie)
            M_U.append(np.dot(np.linalg.pinv(M_U_j_pie), M_inv))

        # 生成K_i、TK_O_i、M_O_i、M_O_i一撇
        K = []
        TK_O1 = []  # 数list
        TK_O2 = []  # 向量list，一个DO对应一个向量，一个向量中的各元素对应各SU
        M_O = []
        M_O_pie = []
        for i in range(DO_num):
            r = Element.random(pairing, Zr)
            K_i = pairing.apply(P, Q) ** r
            # K_i是一个由两个64 bytes长的整数构成的tuple
            # AES加密密钥长度这里只需16 bytes即可
            K.append(eval(hex(K_i[0])[:34]).to_bytes(16, byteorder="big"))

            lambda_O_i = Element.random(pairing, Zr)
            # print("P")
            # print(P)
            # print("Q")
            # print(Q)
            # print("r")
            # print(r)
            # print("K_i")
            # print(K_i)
            # print("e")
            # print(e)
            # print("lambda_O_i")
            # print(lambda_O_i)
            # print("K_i * (e ** lambda_O_i)")
            # print(K_i * (e ** lambda_O_i))
            TK_O1.append(K_i * (e ** lambda_O_i))

            TK_O2_i = []
            for sk_U_j in sk_U:
                TK_O2_i.append(e ** (lambda_O_i * sk_U_j))
            TK_O2.append(TK_O2_i)

            M_O_i = np.random.rand(
                2 * feature_vector_dimension, 2 * feature_vector_dimension
            )
            M_O.append(M_O_i)
            M_O_pie.append(np.dot(np.linalg.pinv(M_O_i), M))

        # 生成γ
        gamma = np.random.randint(1, 20, size=(1, 1))  # p1=19

        return K, K_A, sk_U, pk_U, M_U, M_U_pie, TK_O1, TK_O2, M_O, M_O_pie, gamma

