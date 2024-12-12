from PIL import Image
import numpy as np
import glob
import time


def decimalToBinary(num):
    return format(num, "08b")


# f1_names = glob.glob(r"../dataset/2000/*/*.jpg")
# f1_names = glob.glob(r"./test/*/*.png")
f1_names = glob.glob(r"C:\Users\rtf\Desktop\SVMIS_in_CAEC\adjust\code\test\*\*.png")
label = []
t1 = time.time()
# for k in range(8010, len(f1_names)):
for k in range(len(f1_names)):
    print(f1_names[k])
    im = Image.open(f1_names[k]).convert("L")
    # D:\epcbircode\2000\001.ak47 001_0001
    image_array = np.array(im)
    row, col = image_array.shape

    r = 3.99
    N = row * col
    x = 0.5 + np.zeros(N)
    for n in range(N - 1):
        x[n + 1] = r * x[n] * (1 - x[n])
    y = x.reshape(row, col)
    p = y * 255
    z = p.astype("int64")
    imgg2 = np.zeros(N)
    imgg = imgg2.reshape(row, col)
    for i in range(row):
        for j in range(col):
            p = decimalToBinary(image_array[i][j])
            key = decimalToBinary(z[i][j])
            a = [int(x) for x in str(p)]
            b = [int(x) for x in str(key)]
            string = ""
            for x in range(8):
                string = string + str(a[x] ^ b[x])
            imgg[i][j] = int(string[::-1], 2)

    img2 = Image.fromarray(np.uint8(imgg))
    # img2.show()

    label2 = f1_names[k].split("/")[-1].split(".")[1]
    print(label2)
    label = label2.split("\\")[1]
    # label2 = f1_names[k].split('\\',-1)[4]
    print(label)

    # img2 = img2.save("../enc2000/" + label + ".jpg")
    img2 = img2.save("./enc/" + label + ".jpg")
t2 = time.time()
print("加密图像时间为", (t2 - t1) / 60, "min")
print("finish!")
