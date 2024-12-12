from pymerkle import *
import hashlib
import time
import numpy as np
from base64 import *


def generate_MHT(tree, str_dataset):
    for str_data in str_dataset:
        tree.update(record=str_data)
    # tree.export('backup.json')
    return tree


def generate_proof(tree, query):
    checksum = hashlib.sha256(query).hexdigest()
    proof = tree.auditProof(checksum)
    return proof


def verify(tree, proof):
    commitment = tree.get_commitment()
    validateproof = validateProof(proof, commitment)
    return validateproof


if __name__ == "__main__":
    # query_number = 40 #等于返回的检索结果个数
    database_size = 100000  # 等于图像总数
    database = np.arange(database_size)
    # print("database:", database)
    # str_database = [str(data) for data in database]
    str_database = []
    for data in database:
        str_database.append(b64encode(data))
    # print("str_database:", str_database)
    time1 = time.time()
    tree = MerkleTree(security=False)
    tree = generate_MHT(tree, str_database)
    time2 = time.time()
    print("generating MHT of", database_size, "data needs", time2 - time1, "s")
    for query_number in [5, 10, 20, 30, 40]:
        query = np.random.choice(str_database, query_number, replace=False)
        query_list = query.tolist()
        # print("query_list:", query_list)
        time3 = time.time()
        for i in range(1, 100):
            proofs = []
            for q in query_list:
                # for q in ['12', '13']:
                # print('query_test:', q)
                proofs.append(generate_proof(tree, q))
        time4 = time.time()
        for i in range(1, 1000):
            validateproofs = []
            for proof in proofs:
                verify_results = str(verify(tree, proof))
                validateproofs.append(verify_results)
            # print("validateproofs:", validateproofs)
            # if 'False' in validateproofs:
            # print('Verification Failed! ')
            # else:
            # print('Verification Succeed!')
        time5 = time.time()
        print("----------", query_number, "-----------")
        print(
            "generating verification paths for",
            query_number,
            "queries needs",
            (time4 - time3) / 100 * 1000,
            "ms",
        )
        print("verifying", query_number, "proofs needs", (time5 - time4), "ms")
