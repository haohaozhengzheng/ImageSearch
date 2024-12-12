import time
import numpy as np
from pypbc import *
from pymerkle import *


def EncImage(M_i):
    # TODO: AES encryption
    C_i = []
    for plainimage in M_i:
        if plainimage == "plainimage_1":
            C_i.append("cipherimage_1")
        if plainimage == "plainimage_2":
            C_i.append("cipherimage_2")
        if plainimage == "plainimage_3":
            C_i.append("cipherimage_3")
        if plainimage == "plainimage_4":
            C_i.append("cipherimage_4")
        if plainimage == "plainimage_5":
            C_i.append("cipherimage_5")
    return C_i


def Get_feature_vector(plainimage):
    # TODO
    if plainimage == "plainimage_1":
        feature_vector = np.array(range(1, 11))
    if plainimage == "plainimage_2":
        feature_vector = np.array(range(11, 21))
    if plainimage == "plainimage_3":
        feature_vector = np.array(range(21, 31))
    if plainimage == "plainimage_4":
        feature_vector = np.array(range(31, 41))
    if plainimage == "plainimage_5":
        feature_vector = np.array(range(41, 51))
    return feature_vector


def GenIndex(M_i, M_O_i, gamma):
    F_i = []
    for plainimage in M_i:
        F_i.append(Get_feature_vector(plainimage))

    data2norm = -0.5 * np.linalg.norm(F_i, ord=2, axis=1) ** 2
    f_plus = np.column_stack((F_i, data2norm))
    alpha = np.random.randint(1, 10, size=(len(F_i), feature_vector_dimension - 1))
    f_plusplus = np.concatenate((f_plus, alpha), axis=1)
    varepsilon = np.random.randint(
        0.1, 2, size=(len(F_i), 2 * feature_vector_dimension)
    )
    I_i = np.dot(gamma * f_plusplus + varepsilon, M_O_i)
    return I_i


def GenMHT(C_i, K_A):
    # TODO: using MAC_KA (HMAC?) to generate MHT
    T_i = MerkleTree()
    k = 0  # k=ID(m_{i,k})
    for c in C_i:
        T_i.encryptRecord(str(c + str(k)))
        k += 1
    return T_i


def GenQuery(query_image, gamma):
    q1 = Get_feature_vector(query_image)
    q = np.array(q1).reshape([1, -1])
    q_plus = np.column_stack((q, 1))
    beta = np.random.randint(1, 10, size=(1, feature_vector_dimension - 1))
    q_plusplus = np.concatenate([np.random.randint(1, 10) * q_plus, beta], axis=1)
    vareps = np.random.randint(0.1, 2, size=(1, 2 * feature_vector_dimension))
    Q = np.dot(M_u_j, (gamma * q_plusplus + vareps).T)
    return Q


def Search(I_i, M_O_i_pie, Q, M_U_j_pie):
    converted_indexes = np.dot(I_i, M_O_i_pie)
    converted_query = np.dot(M_U_j_pie, Q)


########################################################################
########################################################################


def Search(cloud_f_i_cipher, user_query_cipher, M_u_j_pie):
    cloud_query_cipher = np.dot(M_u_j_pie, user_query_cipher)
    dis_cipher = []
    dis_cipher1 = np.dot(cloud_f_i_cipher, cloud_query_cipher)
    dis_cipher2 = np.squeeze(dis_cipher1)
    dis_cipher = dis_cipher2
    # print("dis_cipher:", dis_cipher)
    return dis_cipher


if __name__ == "__main__":

    DO_num = 5
    SU_num = 6
    feature_vector_dimension = 10

    plainimage_1 = "plainimage_1"
    plainimage_2 = "plainimage_2"
    plainimage_3 = "plainimage_3"
    plainimage_4 = "plainimage_4"
    plainimage_5 = "plainimage_5"
    image_sets = [
        [plainimage_1, plainimage_2],  # owner1
        [plainimage_3],  # owner2
        [plainimage_4, plainimage_5],  # owner3
    ]

    # 生成双线性对参数
    params = Parameters(qbits=512, rbits=160)
    pairing = Pairing(params)
    P = Element.random(pairing, G1)
    Q = Element.random(pairing, G1)
    e = pairing.apply(P, Q)

    # 生成K_A、矩阵M和它的逆
    K_A = "Message Authentication Code Key"
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
        sk_U.append(Element.random(pairing, Zr))
        pk_U.append(P ** sk_U)
        M_U_j_pie = np.random.rand(
            2 * feature_vector_dimension, 2 * feature_vector_dimension
        )
        M_U_pie.append(M_U_j_pie)
        M_U.append(np.dot(np.linalg.pinv(M_U_j_pie), M_inv))

    # 生成K_i、TK_O_i、M_O_i、M_O_i一撇
    K = []
    TK_O1 = []  # 数list
    TK_O2 = []  # 向量list
    M_O = []
    M_O_pie = []
    for i in range(DO_num):
        r = Element.random(pairing, Zr)
        K_i = pairing.apply(P, Q) ** r
        K.append(K_i)

        lambda_O_i = Element.random(pairing, Zr)
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

    C = []
    gamma = np.random.randint(1, 20, size=(1, 1))
    I = []
    T = []
    for i in range(DO_num):
        C.append(EncImage(image_sets[i]))
        I.append(GenIndex(image_sets[i], M_O[i], gamma))
        T.append(GenMHT(image_sets[i], C[i], K_A))

    m_q = plainimage_4
    Q = GenQuery(m_q, gamma)

    for d in [32, 64, 128, 256, 512]:
        n = 10000  # 有多少个图像
        t1 = time.time()
        gamma, M_o_i, M_o_i_pie, M_u_j, M_u_j_pie = Genkey(d, 100, 1)
        t2 = time.time()
        f = np.random.randint(1, 10, size=(n, d))
        q = f[1]  # 将第二个特征向量作为query
        t3 = time.time()
        owner_index_cipher = GenIndex_owner(f, M_o_i, gamma)
        t4 = time.time()
        cloud_index_cipher = GenIndex_cloud(owner_index_cipher, M_o_i_pie)
        t5 = time.time()
        for i in range(1, 1000):
            user_query_cipher = GenQuery_user(q, M_u_j, gamma)
        t6 = time.time()
        dis_cipher = Search(cloud_index_cipher, user_query_cipher, M_u_j_pie)
        t7 = time.time()
        print("-------------", d, "-------------", n, "-------------")
        print("Genkey time(ms):", (t2 - t1) * 1000)
        print("GenIndex time(ms):", (t4 - t3) * 1000)
        print("GenQuery time(ms):", (t6 - t5) * 1000 / 1000)
        print("Search time(ms):", (t7 - t6 + t5 - t4) * 1000)

