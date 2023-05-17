import os
import cv2

path = "./static/exp"  # jpg图片和对应的生成结果的txt标注文件，放在一起
path3 = "./static/output"  # 裁剪出来的小图保存的根目录
w = 256  # 原始图片resize
h = 256
img_total = []
txt_total = []

file = os.listdir(path)
for filename in file:
    first, last = os.path.splitext(filename)
    if last == ".jpg":  # 图片的后缀名
        img_total.append(first)
    else:
        txt_total.append(first)

for img_ in img_total:
    if img_ in txt_total:
        filename_img = img_ + ".jpg"  # 图片的后缀名
        path1 = os.path.join(path, filename_img)
        img = cv2.imread(path1)
        h, w = img.shape[0], img.shape[1]
        filename_txt = img_ + ".txt"
        n = 1
        with open(os.path.join(path, filename_txt), "r+", encoding="utf-8", errors="ignore") as f:
            for line in f:
                aa = line.split(" ")
                x_center = w * float(aa[1])  # aa[1]左上点的x坐标
                y_center = h * float(aa[2])  # aa[2]左上点的y坐标
                width = int(w * float(aa[3]))  # aa[3]图片width
                height = int(h * float(aa[4]))  # aa[4]图片height
                lefttopx = int(x_center - width / 2.0)
                lefttopy = int(y_center - height / 2.0)
                roi = img[lefttopy + 1:lefttopy + height + 3,
                      lefttopx + 1:lefttopx + width + 1]  # [左上y:右下y,左上x:右下x] (y1:y2,x1:x2)需要调参，否则裁剪出来的小图可能不太好
                print('roi:', roi)  # 如果不resize图片统一大小，可能会得到有的roi为[]导致报错
                filename_last = img_ + "_" + str(n) + ".jpg"  # 裁剪出来的小图文件名
                print(filename_last)
                path2 = os.path.join(path3)  # 需要在path3路径下创建一个roi文件夹
                print('path2:', path2)  # 裁剪小图的保存位置
                cv2.imwrite(os.path.join(path3, filename_last), roi)
                n = n + 1
    else:
        continue
