#!/usr/bin/env python3
# make  background.npz
import os

import cv2
import numpy as np
import urllib.request

from img2str import img_hist, img_to_sig, img_merge, make_img4hist

aadb_url = "https://raw.githubusercontent.com/atlasacademy/aa-db/master/build/assets/list/"
img_dir = "data/misc/"
gold_flame = img_dir + "listframes3_bg.png"
silver_flame = img_dir + "listframes2_bg.png"
bronze_flame = img_dir + "listframes1_bg.png"
zero_flame = img_dir + "listframes0_bg.png"

file_gold = "data/misc/gold.png"
file_silver = "data/misc/silver.png"
file_bronze = "data/misc/bronze.png"
file_zero = "data/misc/zero.png"
output = "background.npz"

# 余白を落して拡大して保存
def download_file(url, filename):
    try:
        with urllib.request.urlopen(url + filename) as web_file:
            data = web_file.read()
            with open(img_dir  + filename, mode='wb') as local_file:
                local_file.write(data)
    except urllib.error.URLError as e:
        print(e)

def makeimg(file):
    img = cv2.imread(file)
    h, w = img.shape[:2]
    img = img[5: h-5, 5: w-5]

    #横幅188に拡大
    SIZE = 314
    img = cv2.resize(img, (0, 0),
            fx=SIZE/(w - 10), fy=SIZE/(w - 10),
            interpolation=cv2.INTER_AREA)

    return img


def main():
    for i in range(4):
        download_file(aadb_url, "listframes" + str(i) + "_bg.png")
    img_zero = make_img4hist(makeimg(zero_flame))
    target_hist = img_hist(img_zero)
    sig_zero = img_to_sig(target_hist)

    img_gold = make_img4hist(makeimg(gold_flame))
    target_hist = img_hist(img_gold)
    sig_gold = img_to_sig(target_hist)

    img_silver = make_img4hist(makeimg(silver_flame))
    target_hist = img_hist(img_silver)
    sig_silver = img_to_sig(target_hist)

    img_bronze = make_img4hist(makeimg(bronze_flame))
    target_hist = img_hist(img_bronze)
    sig_bronze = img_to_sig(target_hist)

    np.savez(output,
             sig_zero=sig_zero,
             sig_gold=sig_gold,
             sig_silver=sig_silver,
             sig_bronze=sig_bronze)

if __name__ == '__main__':
    os.makedirs(img_dir, exist_ok=True)
    main()
