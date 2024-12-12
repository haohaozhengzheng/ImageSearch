import os
import time
import numpy as np
from keras.applications.resnet import ResNet50
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from sklearn.decomposition import PCA


def load_data(file):
    img_pathes = []
    for path, dirs, files in os.walk(file):
        img_pathes.extend([os.path.join(path, file) for file in files])
    return img_pathes


def ext_feat(paths):
    model = ResNet50(weights="imagenet", include_top=False, pooling="avg")
    features = np.zeros(2048)
    for path in paths:
        img = image.load_img(path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        feature = model.predict(x)  # [1,512]
        aaa = np.squeeze(feature)  # [1,512]
        # print("aaa:", aaa)
        # bbb = aaa.reshape(1, 25088)#[1,25088]
        features = np.row_stack((features, aaa))
    features = np.delete(features, 0, axis=0)

    pca = PCA(n_components=7)
    features = pca.fit_transform(features)
    return features


if __name__ == "__main__":
    # os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

    img_file = "../dataset/2000"
    features_file = "D:\epcbircode/trapdoor_features_512.csv"

    t1 = time.time()
    img_paths = load_data(img_file)
    feats = ext_feat(img_paths)
    np.savetxt(features_file, feats)
    t2 = time.time()

    for i in range(len(feats)):
        print(labels[i], feats[i])
    print("extract", len(feats), "features:", (t2 - t1) / 60, "min")
    print("finish!")
