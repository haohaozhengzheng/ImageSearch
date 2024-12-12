import numpy as np


class CS:
    def __init__(self, M_O_pie, M_U_pie) -> None:
        self.M_O_pie = M_O_pie
        self.M_U_pie = M_U_pie
        self.index_received_from_EDS = {}
        self.query_passed_by_EDS = {}
        self.ranking_result = None

    def Receive_from_EDS(self, index_from_EDS, query_passed_by_EDS):
        self.index_received_from_EDS = {
            **self.index_received_from_EDS,
            **index_from_EDS,
        }  # 把新的dict合并入原来的dict
        self.query_passed_by_EDS = query_passed_by_EDS

    def Search(self, gamma, p_1):
        for EDS_DO_ID, I_i in self.index_received_from_EDS.items():
            self.index_received_from_EDS[EDS_DO_ID] = np.dot(
                I_i, self.M_O_pie[EDS_DO_ID[1]]
            )  # convert indexes
        for EDS_SU_ID, Q in self.query_passed_by_EDS.items():
            self.query_passed_by_EDS[EDS_SU_ID] = np.dot(
                self.M_U_pie[EDS_SU_ID[1]], Q
            )  # convert query

        sorted_image_list = []
        for EDS_DO_ID, I_i in self.index_received_from_EDS.items():
            i = 0
            for row in I_i:
                sorted_image_list.append(((EDS_DO_ID, i), row))
                i += 1
        sorted_image_list.sort(
            key=lambda image: np.rint(
                np.dot(image[1], list(self.query_passed_by_EDS.values())[0])
                / gamma ** 2
            )
            % p_1
        )
        self.ranking_result = (
            sorted_image_list  # [(((EDS_ID, DO_ID), image_ID), index)]
        )

    def Send_Ranking2EDS(self, EDS_ID):
        return [
            (x[0][0][1], x[0][1], self.ranking_result.index(x))
            for x in self.ranking_result
            if x[0][0][0] == EDS_ID
        ]  # 返回属于该EDS的[(DO_ID, image_ID, ranking_position)]
