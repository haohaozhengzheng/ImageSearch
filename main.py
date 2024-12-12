import os
import time

from KGS import KGS
from DO import DO
from EDS import EDS
from SU import SU
from CS import CS


def main():
    feature_vector_dimension = 7
    print("The KGS is generating parameters...")
    t_KGS_start = time.time()
    key_generation_center = KGS()
    (
        K,  # 图像加密密钥，一个DO一个
        K_A,  # MAC key，常量
        sk_U,  # SU私钥，一个SU一个
        pk_U,  # SU公钥，一个SU一个
        M_U,  # 矩阵M_U_j，一个SU一个
        M_U_pie,  # 矩阵M_U_j一撇，一个SU一个
        TK_O1,  # TK_O的第一个元素，一个DO一个
        TK_O2,  # TK_O的第二个元素，一个DO一个
        M_O,  # 矩阵M_O_i，一个DO一个
        M_O_pie,  # 矩阵M_O_i一撇，一个DO一个
        gamma,  # DO、SU、CS都要用到
    ) = key_generation_center.GenKey(
        3, 2, feature_vector_dimension, "Message Authentication Code Key",
    )
    # print(TK_O1)
    # print(TK_O2)
    t_KGS_finish = time.time()
    print("Done in", t_KGS_finish - t_KGS_start, "s!\n")

    all_images_path = "../dataset/2000"
    all_images = []
    for path, dirs, files in os.walk(all_images_path):
        all_images.extend([os.path.join(path, file) for file in files])
    data_owner0_image_set = all_images[:50]
    data_owner1_image_set = all_images[50:100]
    data_owner2_image_set = all_images[100:150]

    print(
        "Data owners are generating their cipher images, encrypted indexes and MHTs, and send them to the nearest EDS..."
    )
    t_DO_start = time.time()
    data_owner0 = DO(
        0, data_owner0_image_set, K[0], M_O[0], K_A, gamma, feature_vector_dimension
    )
    data_owner1 = DO(
        1, data_owner1_image_set, K[1], M_O[1], K_A, gamma, feature_vector_dimension
    )
    data_owner2 = DO(
        2, data_owner2_image_set, K[2], M_O[2], K_A, gamma, feature_vector_dimension
    )

    # TODO: find nearest EDS
    # 这里假定离DO0最近的为EDS0，离DO1和DO2最近的为EDS1
    edge_server0 = EDS(0)
    edge_server1 = EDS(1)
    edge_server0.Receive_DO_Information(TK_O1[0], TK_O2[0], *(data_owner0.Send2EDS()))
    edge_server1.Receive_DO_Information(TK_O1[1], TK_O2[1], *(data_owner1.Send2EDS()))
    edge_server1.Receive_DO_Information(TK_O1[2], TK_O2[2], *(data_owner2.Send2EDS()))
    t_DO_finish = time.time()
    print("Done in", t_DO_finish - t_DO_start, "s!\n")

    # 假定离SU0最近的为EDS1
    print(
        "SU is generating the encrypted query and sending it to the nearest EDS, and CS is asked by the EDS to do the ranking job..."
    )
    t_SU_start = time.time()
    search_user0 = SU(0)
    edge_server1.Receive_SU_Information(
        *(
            search_user0.GenQuery(
                "../dataset/2000/002.american-flag/002_0017.jpg",
                gamma,
                M_U[0],
                feature_vector_dimension,
            )
        )
    )

    cloud_server = CS(M_O_pie, M_U_pie)
    cloud_server.Receive_from_EDS(*(edge_server0.Send2CS()))
    cloud_server.Receive_from_EDS(*(edge_server1.Send2CS()))

    cloud_server.Search(gamma, 19)
    t_CS_finish = time.time()
    print("Done in", t_CS_finish - t_SU_start, "s!\n")

    print("CS sends the result to EDSs, and the EDSs send the result to SU...")
    search_user0.Receive_from_EDS(
        edge_server0.Receive_Ranking_Result_from_CS_and_Send2SU(
            cloud_server.Send_Ranking2EDS(0), 0
        )
    )
    search_user0.Receive_from_EDS(
        edge_server1.Receive_Ranking_Result_from_CS_and_Send2SU(
            cloud_server.Send_Ranking2EDS(1), 0
        )
    )
    search_user0.Receive_trusted_MHT_root_from_DO(data_owner0.Send_MHT_Root2SU())
    search_user0.Receive_trusted_MHT_root_from_DO(data_owner1.Send_MHT_Root2SU())
    search_user0.Receive_trusted_MHT_root_from_DO(data_owner2.Send_MHT_Root2SU())

    search_user0.Verify_and_DecImage(sk_U[0])


if __name__ == "__main__":
    main()
