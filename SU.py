import os

import numpy as np
from pymerkle import *
from Cryptodome.Cipher import AES
from DO import Get_feature_vector


class SU:
    def __init__(self, SU_ID) -> None:
        self.SU_ID = SU_ID
        self.cipher_image_info_list = []
        self.trusted_MHT_root = {}  # {DO_ID: rootHash}
        self.final_plainimage_rank = {}  # {plainimage: ranking_position}

    def GenQuery(self, query_image, gamma, M_U_j, feature_vector_dimension):
        # TODO: 要可生成单独一张图片的特征向量，而不依赖数据集中其他图片
        # 即希望能：q1 = Get_feature_vector([query_image], feature_vector_dimension)

        all_images_path = "../dataset/2000"
        all_images = []
        for path, dirs, files in os.walk(all_images_path):
            all_images.extend([os.path.join(path, file) for file in files])
        entire_feature_matrix, entire_mapping = Get_feature_vector(
            all_images, feature_vector_dimension
        )
        q1 = entire_feature_matrix[entire_mapping[query_image]]

        q = np.array(q1).reshape([1, -1])
        q_plus = np.column_stack((q, 1))
        beta = np.random.randint(1, 10, size=(1, len(q[0]) - 1))  # p2=9
        q_plusplus = np.concatenate([np.random.randint(1, 10) * q_plus, beta], axis=1)
        vareps = np.random.randint(0.1, 2, size=(1, 2 * len(q[0])))
        Q = np.dot(M_U_j, (gamma * q_plusplus + vareps).T)
        return self.SU_ID, Q

    def Receive_from_EDS(self, cipher_image_info):
        self.cipher_image_info_list += cipher_image_info

    def Receive_trusted_MHT_root_from_DO(self, DO_root):
        self.trusted_MHT_root = {**self.trusted_MHT_root, **DO_root}

    def Verify_and_DecImage(self, sk_U_j):
        # print(self.cipher_image_info_list)
        for cipher_image_info in self.cipher_image_info_list:
            if validateProof(
                cipher_image_info[-1], self.trusted_MHT_root[cipher_image_info[1]]
            ):
                # DecImage
                sk_U_j_inv = sk_U_j ** -1
                TK_2_inv = (cipher_image_info[4]) ** sk_U_j_inv
                K_i = cipher_image_info[3] - TK_2_inv

                K_i = eval(hex(K_i[0])[:34]).to_bytes(16, byteorder="big")

                cipher_module = AES.new(
                    K_i, AES.MODE_EAX, nonce=cipher_image_info[5][0]
                )
                recovered = cipher_module.decrypt_and_verify(
                    cipher_image_info[5][1], cipher_image_info[5][2]
                )

                self.final_plainimage_rank[recovered] = cipher_image_info[2]

                # if cipher_image_info[5] == "cipherimage_1":
                #     self.final_plainimage_rank["plainimage_1"] = cipher_image_info[2]
                # if cipher_image_info[5] == "cipherimage_2":
                #     self.final_plainimage_rank["plainimage_2"] = cipher_image_info[2]
                # if cipher_image_info[5] == "cipherimage_3":
                #     self.final_plainimage_rank["plainimage_3"] = cipher_image_info[2]
                # if cipher_image_info[5] == "cipherimage_4":
                #     self.final_plainimage_rank["plainimage_4"] = cipher_image_info[2]
                # if cipher_image_info[5] == "cipherimage_5":
                #     self.final_plainimage_rank["plainimage_5"] = cipher_image_info[2]

        # print("The final ranking received by the search user:\n--------------------")
        for image in dict(
            sorted(self.final_plainimage_rank.items(), key=lambda item: item[1])
        ).items():
            # print("%d\t%s" % (image[1] + 1, image[0]))
            with open(
                "./ranking_result/" + str(image[1]) + ".jpg", "wb"
            ) as recovered_image:
                recovered_image.write(image[0])
        print(
            'The final ranking received by the search user is stored in the "./ranking_result/" directory.'
        )
