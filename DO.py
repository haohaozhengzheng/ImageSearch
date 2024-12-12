import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# import time

import numpy as np
from keras.applications.resnet import ResNet50
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from sklearn.decomposition import PCA

from Cryptodome.Cipher import AES
from pymerkle import *


def EncImage(M_i, K_i):
    C_i = []

    for plain_image_path in M_i:
        with open(plain_image_path, "rb") as plainimage:
            plainimage_data = plainimage.read()
        cipher_module = AES.new(K_i, AES.MODE_EAX)
        nonce = cipher_module.nonce
        cipher_image, tag = cipher_module.encrypt_and_digest(plainimage_data)
        C_i.append((nonce, cipher_image, tag))
    return C_i

    # C_i = []
    # for plainimage in M_i:
    #     if plainimage == "plainimage_1":
    #         C_i.append("cipherimage_1")
    #     if plainimage == "plainimage_2":
    #         C_i.append("cipherimage_2")
    #     if plainimage == "plainimage_3":
    #         C_i.append("cipherimage_3")
    #     if plainimage == "plainimage_4":
    #         C_i.append("cipherimage_4")
    #     if plainimage == "plainimage_5":
    #         C_i.append("cipherimage_5")
    # return C_i


def Get_feature_vector(M_i, feature_vector_dimension):
    mapping_dict = {}  # 记录特征向量矩阵features中第i行对应的图片路径{path: i}

    model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
    features = np.zeros(2048)
    i = 0
    for plain_image in M_i:
        img = image.load_img(plain_image, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        feature = model.predict(x)
        aaa = np.squeeze(feature)
        features = np.row_stack((features, aaa))

        mapping_dict[plain_image] = i
        i += 1
    features = np.delete(features, 0, axis=0)
    pca = PCA(n_components=feature_vector_dimension)
    features = pca.fit_transform(features)
    return features, mapping_dict


def GenIndex(M_i, M_O_i, gamma, feature_vector_dimension):
    F_i = Get_feature_vector(M_i, feature_vector_dimension)[0]

    data2norm = -0.5 * np.linalg.norm(F_i, ord=2, axis=1) ** 2
    f_plus = np.column_stack((F_i, data2norm))
    alpha = np.random.randint(1, 10, size=(len(M_i), len(F_i[0]) - 1))  # p2=9
    f_plusplus = np.concatenate((f_plus, alpha), axis=1)
    varepsilon = np.random.randint(0.1, 2, size=(len(M_i), 2 * len(F_i[0])))
    I_i = np.dot(gamma * f_plusplus + varepsilon, M_O_i)
    return I_i


class DO:
    def __init__(
        self, DO_ID, M_i, K_i, M_O_i, K_A, gamma, feature_vector_dimension
    ) -> None:
        self.DO_ID = DO_ID
        self.M_i = M_i
        self.K_i = K_i
        self.M_O_i = M_O_i
        self.K_A = K_A
        self.gamma = gamma

        self.C_i = EncImage(M_i, K_i)
        self.I_i = GenIndex(M_i, M_O_i, gamma, feature_vector_dimension)
        self.T_i = self.GenMHT(self.C_i, K_A)

    def GenMHT(self, C_i, K_A):
        # TODO: using MAC_KA (HMAC?) to generate MHT
        T_i = MerkleTree(security=False)
        k = 0  # ID(m_{i,k})为：DO ID-image ID
        for c in C_i:
            T_i.encryptRecord(str(c) + str(self.DO_ID) + "-" + str(k))
            k += 1
        return T_i

    def Send2EDS(self):
        return self.DO_ID, self.C_i, self.I_i, self.T_i

    def Send_MHT_Root2SU(self):
        return {self.DO_ID: self.T_i.get_commitment()}
