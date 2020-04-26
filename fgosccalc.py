#!/usr/bin/env python3
import sys
import cv2
import numpy as np
from pathlib import Path
from collections import Counter
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
    newdic = {}
    for item in tmplist:
        newdic[item[0]] = item[1] * n

    return newdic

#恒常アイテム
#ここに記述したものはドロップ数を読み込まない
#順番ルールにも使われる
# 通常 弓→槍の順番だが、種火のみ槍→弓の順番となる
# 同じレアリティの中での順番ルールは不明
std_item = ['実', 'カケラ', '卵', '鏡','炉心', '神酒', '胆石', '産毛', 'スカラベ',    
    'ランプ', '幼角', '根', '逆鱗', '心臓', '爪', '脂', '涙石' , 
    '霊子', '冠', '矢尻', '鈴', 'オーロラ',  '指輪', '結氷', '勾玉','貝殻', '勲章', 
    '種', 'ランタン', '八連', '宝玉', '羽根', '頁', '歯車', 'ホム', '蹄鉄',
    '火薬', '鉄杭', '髄液', '毒針', '鎖', '塵', '牙', '骨', '証', 
    '剣秘', '弓秘', '槍秘', '騎秘', '術秘', '殺秘', '狂秘',
    '剣魔', '弓魔', '槍魔', '騎魔', '術魔', '殺魔', '狂魔',
    '剣輝', '弓輝', '槍輝', '騎輝', '術輝', '殺輝', '狂輝',
    '剣モ', '弓モ', '槍モ', '騎モ', '術モ', '殺モ', '狂モ',
    '剣ピ', '弓ピ', '槍ピ', '騎ピ', '術ピ', '殺ピ', '狂ピ',
    '全種火', '全灯火', '全大火', '"全猛火','全業火',
    '剣種火', '剣灯火', '剣大火', '剣猛火', '剣業火',
    '槍種火', '槍灯火', '槍大火', '槍猛火', '槍業火',
    '弓種火', '弓灯火', '弓大火', '弓猛火', '弓業火',
    '騎種火', '騎灯火', '騎大火', '騎猛火', '騎業火',
    '術種火', '術灯火', '術大火', '術猛火', '術業火',
    '殺種火', '殺灯火', '殺大火', '殺猛火', '殺業火',
    '狂種火', '狂灯火', '狂大火', '狂猛火', '狂業火',
]


monyupi_list = ['剣モ', '弓モ', '槍モ', '騎モ', '術モ', '殺モ', '狂モ',
                '剣ピ', '弓ピ', '槍ピ', '騎ピ', '術ピ', '殺ピ', '狂ピ', ]

skillstone_list = [ '剣秘', '弓秘', '槍秘', '騎秘', '術秘', '殺秘', '狂秘',
                    '剣魔', '弓魔', '槍魔', '騎魔', '術魔', '殺魔', '狂魔',
                    '剣輝', '弓輝', '槍輝', '騎輝', '術輝', '殺輝', '狂輝']
    
tanebi_list = [ '全種火', '全灯火', '全大火', '"全猛火','全業火',
                '剣種火', '剣灯火', '剣大火', '剣猛火', '剣業火',
                '槍種火', '槍灯火', '槍大火', '槍猛火', '槍業火',
                '弓種火', '弓灯火', '弓大火', '弓猛火', '弓業火',
                '騎種火', '騎灯火', '騎大火', '騎猛火', '騎業火',
                '術種火', '術灯火', '術大火', '術猛火', '術業火',
                '殺種火', '殺灯火', '殺大火', '殺猛火', '殺業火',
                '狂種火', '狂灯火', '狂大火', '狂猛火', '狂業火']


if __name__ == '__main__':
    dropitems = img2str.DropItems()        
    svm = cv2.ml.SVM_load(str(img2str.training))
    file1 = Path(sys.argv[1])
    img_rgb = img2str.imread(str(file1))
    sc1 = img2str.ScreenShot(img_rgb, svm, dropitems)

    file2 = Path(sys.argv[2])
    img_rgb = img2str.imread(str(file2))
    sc2 = img2str.ScreenShot(img_rgb, svm, dropitems)

    newdic = make_diff(sc1.itemlist, sc2.itemlist)
    std_item_dic = {}
    for i in std_item:
        std_item_dic[dropitems.normalize_item(i)] = 0

    monyupi_flag = False
    skillstone_flag = False
    tanebi_flag = False
    output = ""
    if sc2.quest_output != "":
        output = "【" + sc2.quest_output + "】000周\n"
        droplist = sc2.droplist
    elif sc1.quest_output != "":
        output = "【" + sc1.quest_output + "】000周\n"
        droplist = sc1.droplist
    else:
        output = "【(クエスト名)】000周\n"
        droplist = ""
    std_item_dic.update(dict(Counter(droplist)))
    for key in list(std_item_dic.keys()):
        if std_item_dic[key] == 0:
            del std_item_dic[key]

    for item in std_item_dic.keys():
        if skillstone_flag == False and item in skillstone_list:
            output = output[:-1] + "\n"
            skillstone_flag = True
        elif skillstone_flag == True and item not in skillstone_list:
            output = output[:-1] + "\n"
            skillstone_flag = False

        if monyupi_flag == False and item in monyupi_list:
            output = output[:-1] + "\n"
            monyupi_flag = True
        elif monyupi_flag == True and item not in monyupi_list:
            output = output[:-1] + "\n"
            monyupi_flag = False

        if tanebi_flag == False and item in tanebi_list:
            output = output[:-1] + "\n"
            tanebi_flag = True
        elif tanebi_flag == True and item not in tanebi_list:
            output = output[:-1] + "\n"
            tanebii_flag = False

        if item in newdic:
            output = output + item + str(newdic[item]) + '-'
        else:
            output = output + item + 'NaN-'            
##        output = output + item[0] + str(item[1]) + '-'

    if len(output) > 0:
        output = output[:-1]
    print(output)
    print("#FGO周回カウンタ http://aoshirobo.net/fatego/rc/")
