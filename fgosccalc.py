#!/usr/bin/env python3
import sys
import cv2
import numpy as np
from pathlib import Path
import img2str


def make_diff(itemlist1, itemlist2):
    tmplist = []
    for before, after in zip(itemlist1, itemlist2):
            if before[1].isdigit() and after[1].isdigit() and (not before[0].startswith("未ドロップ") and not after[0].startswith("未ドロップ")):
                tmplist.append((after[0], int(after[1])-int(before[1])))
    result = ""
    sum = 0
    for item in tmplist:
        sum = sum + item[1]
    if sum < 0:
        n = -1
    else:
        n = 1
    newlist = []
    for item in tmplist:
        newlist.append((item[0], item[1] * n))

    return newlist
    
if __name__ == '__main__':
    dropitems = img2str.DropItems()        
    svm = cv2.ml.SVM_load(str(img2str.training))
    file1 = Path(sys.argv[1])
    img_rgb = img2str.imread(str(file1))
    sc1 = img2str.ScreenShot(img_rgb, svm, dropitems)

    file2 = Path(sys.argv[2])
    img_rgb = img2str.imread(str(file2))
    sc2 = img2str.ScreenShot(img_rgb, svm, dropitems)

    new_list = make_diff(sc1.itemlist, sc2.itemlist)
    result = ""
    for item in new_list:
        result = result + item[0] + str(item[1]) + '-'
    if len(result) > 0:
        print(result[:-1])
