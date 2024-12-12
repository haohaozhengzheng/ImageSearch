import hashlib
from pymerkle import *


def GenProof(tree, leaf):
    checksum = hashlib.sha256(leaf).hexdigest()
    proof = tree.auditProof(checksum)
    return proof


class EDS:
    def __init__(self, EDS_ID) -> None:
        self.EDS_ID = EDS_ID
        self.O_i_Information_Dict = {}
        self.U_j_Query_Dict = {}

    def Receive_DO_Information(self, TK_O1_i, TK_O2_i, DO_ID, C_i, I_i, T_i):
        self.O_i_Information_Dict[(self.EDS_ID, DO_ID)] = [
            TK_O1_i,
            TK_O2_i,
            C_i,
            I_i,
            T_i,
        ]

    def Receive_SU_Information(self, SU_ID, Q):
        self.U_j_Query_Dict[(self.EDS_ID, SU_ID)] = Q

    def Send2CS(self):
        index_send2CS = {}
        for key, value in self.O_i_Information_Dict.items():
            index_send2CS[key] = value[3]  # {(EDS_ID, DO_ID): I_i}
        return index_send2CS, self.U_j_Query_Dict

    def Receive_Ranking_Result_from_CS_and_Send2SU(self, partial_ranking, SU_ID):
        return [
            (  # TABLE VI
                self.EDS_ID,  # EDS identity
                rank_image[0],  # DO_ID
                rank_image[2],  # ranking position
                self.O_i_Information_Dict[(self.EDS_ID, rank_image[0])][0],  # TK_O1_i
                self.O_i_Information_Dict[(self.EDS_ID, rank_image[0])][1][
                    SU_ID
                ],  # 针对ID为SU_ID的SU的TK_O2_i
                self.O_i_Information_Dict[(self.EDS_ID, rank_image[0])][2][
                    rank_image[1]
                ],  # C_i中指定的那个图像
                GenProof(
                    self.O_i_Information_Dict[(self.EDS_ID, rank_image[0])][4],
                    (
                        str(
                            self.O_i_Information_Dict[(self.EDS_ID, rank_image[0])][2][
                                rank_image[1]
                            ]
                        )
                        + str(rank_image[0])
                        + "-"
                        + str(rank_image[1])
                    ).encode("utf-8"),
                ),
            )
            for rank_image in partial_ranking
        ]
