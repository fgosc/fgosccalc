#!/usr/bin/env python3
import sys
import cv2
from pathlib import Path
import numpy as np

progname = "img2str"
version = "0.0.1"


training = Path(__file__).resolve().parent / Path("property.xml") #アイテム下部

class DropItems:
    Item_dir = Path(__file__).resolve().parent / Path("item/")
    hasher = cv2.img_hash.PHash_create()


    #恒常アイテムのハッシュ値
    dist_item ={
        'QP':np.array([[214,  27,  77, 212,  33, 165,  72, 134]], dtype='uint8'),
        '爪':np.array([[250,  14, 161,  65,  22, 225, 125,  12]], dtype='uint8'),
        '心臓':np.array([[246,  14,  39, 163,  41, 179,  24,   9]], dtype='uint8'),
        '逆鱗':np.array([[ 30,  14, 225, 248,  33, 145, 135,  17]], dtype='uint8'),
        '根':np.array([[30, 67, 225, 44, 27, 89, 134, 148]], dtype='uint8'),
        '幼角':np.array([[30,  99, 233,  94,  51, 141,  22, 147]], dtype='uint8'),
        '涙石':np.array([[54,  97,  73,  24, 135,   4,  73,  20]], dtype='uint8'),
        '脂':np.array([[ 86,  44,   5,   3,   1,  89, 227,   2]], dtype='uint8'),
        'ランプ':np.array([[102,  41, 143, 153, 148,  99,  52,  88]], dtype='uint8'),
        'スカラベ':np.array([[36, 47, 157, 70, 3, 80, 99, 48]], dtype='uint8'),
        '産毛':np.array([[ 92, 163,  71,  24,  91, 173, 133, 100]], dtype='uint8'),
        '胆石':np.array([[214,  19, 129,  76,  35, 138, 188,  81]], dtype='uint8'),
        '神酒':np.array([[118,  25,  20, 108, 227, 129,  81, 155]], dtype='uint8'),
        '炉心':np.array([[70,  51, 141,  28,  11,  39,  89, 140]], dtype='uint8'),
        '鏡':np.array([[ 22,  75, 181,  92,  20,  83, 138,   4]], dtype='uint8'),
        '卵':np.array([[54,  50,  33,  12,  73, 197,  17,  97]], dtype='uint8'),
        'カケラ':np.array([[118, 163,   5,  12, 233, 148,  73,  38]], dtype='uint8'),
        '種':np.array([[126, 33, 5, 120, 161, 94, 81, 20]], dtype='uint8'),
        'ランタン':np.array([[166, 152, 137,  89, 146,  17, 164, 196]], dtype='uint8'),
        '八連':np.array([[206,  81,  61, 174, 129,  26,  97,  22]], dtype='uint8'),
        '宝玉':np.array([[92,  72, 141, 151, 194, 225, 176, 167]], dtype='uint8'),
        '羽根':np.array([[62, 162, 161, 221, 28, 73, 105, 101]], dtype='uint8'),
        '歯車':np.array([[60, 222, 7, 1, 225, 113, 121, 165]], dtype='uint8'),
        '頁':np.array([[23,  56, 175, 194, 236, 115, 102, 236]], dtype='uint8'),
        'ホム':np.array([[214,   1,   3,  88,  12, 132, 163, 114]], dtype='uint8'),
        '蹄鉄':np.array([[248, 137,  23,  82, 163, 180, 123,  60]], dtype='uint8'),
        '勲章':np.array([[182,  18,  90, 232,   9, 173, 165,  37]], dtype='uint8'),
        '貝殻':np.array([[122, 106, 165, 149, 201, 72, 27, 148]], dtype='uint8'),
        '勾玉':np.array([[25, 20, 255, 234, 4, 27, 216, 166]], dtype='uint8'),
        '結氷':np.array([[94,  67,  29, 232, 196,  28, 179, 206]], dtype='uint8'),
        '指輪':np.array([[218, 225,   7,   9,   5,  98, 137, 115]], dtype='uint8'),
        'オーロラ':np.array([[92,   3, 233, 148,  92,  37, 153,  33]], dtype='uint8'),
        '鈴':np.array([[202,  67,  29,  32,  19,  44,  17, 202]], dtype='uint8'),
        '矢尻':np.array([[244,  47, 139,  64,  43,  41, 218, 217]], dtype='uint8'),
        '冠':np.array([[47, 168, 253, 102, 137, 252, 114, 169]], dtype='uint8'),
        '証':np.array([[86, 7, 5, 1, 97, 88, 14, 6]], dtype='uint8'),
        '骨':np.array([[90,  83,  88,  77, 101, 149, 213,  81]], dtype='uint8'),
        '牙':np.array([[82,  83,   4, 181,  17,  25, 141, 241]], dtype='uint8'),
        '塵':np.array([[28, 5, 5, 64, 89, 92, 5, 4]], dtype='uint8'),
        '鎖':np.array([[254,  15,   1,  33,  49, 208,   9,  45]], dtype='uint8'),
        '毒針':np.array([[82, 181, 165, 105,  75,  91,  19, 179]], dtype='uint8'),
        '髄液':np.array([[ 54, 105, 211, 166,  76,  27,  44,  24]], dtype='uint8'),
        '鉄杭':np.array([[ 28,  29,  56,  51,  99, 131,   3,   7]], dtype='uint8'),
        '火薬':np.array([[90, 167,  17,  41,  48,  29, 141, 225]], dtype='uint8'),
        '剣秘':np.array([[232, 26, 150, 166, 67, 123, 119, 168]], dtype='uint8'),
        '弓秘':np.array([[232,  30, 118, 130,   7, 115, 101, 152]], dtype='uint8'),
        '槍秘':np.array([[232,  30, 214, 179,  71, 220, 189,  96]], dtype='uint8'),
        '騎秘':np.array([[226,  26, 158, 166,  71, 121, 247, 184]], dtype='uint8'),
        '術秘':np.array([[232, 22, 94, 137, 71, 118, 125, 200]], dtype='uint8'),
        '殺秘':np.array([[232,  26, 150, 102,  70, 187, 121, 232]], dtype='uint8'),
        '狂秘':np.array([[232,  26,  86, 102,   6,  59, 117, 136]], dtype='uint8'),
        '剣魔':np.array([[86, 131, 165, 241, 161, 24, 9, 28]], dtype='uint8'),
        '弓魔':np.array([[86,   3, 133, 225,  33,  24,  25,  28]], dtype='uint8'),
        '槍魔':np.array([[86,   3, 133, 201, 161, 113,  73,  28]], dtype='uint8'),
        '騎魔':np.array([[94,   3, 165, 225, 169,  80,   9,  28]], dtype='uint8'),
        '術魔':np.array([[94,   3, 165, 241, 169,  88,  41,  24]], dtype='uint8'),
        '殺魔':np.array([[86,   3, 165, 241, 169, 120,   9,  24]], dtype='uint8'),
        '狂魔':np.array([[86,   3, 133, 177, 169,  88,   9,  28]], dtype='uint8'),
        '剣輝':np.array([[30, 3, 5, 41, 105, 18, 81, 4]], dtype='uint8'),
        '弓輝':np.array([[118,  67, 133,  41, 105,  18,  16,   4]], dtype='uint8'),
        '槍輝':np.array([[118,  67,   5,  41, 121,  82,  73, 148]], dtype='uint8'),
        '騎輝':np.array([[94,  67,   5,  41, 233,  82,  25, 132]], dtype='uint8'),
        '術輝':np.array([[126,   3, 135,  33, 105,  90,  81,  20]], dtype='uint8'),
        '殺輝':np.array([[126,  67,   5, 185, 121,  82,  16, 148]], dtype='uint8'),
        '狂輝':np.array([[126,  71,   5, 185, 105,  82,  24,   4]], dtype='uint8'),
        '剣モ':np.array([[22, 41, 227, 152, 75, 140, 204, 18]], dtype='uint8'),
        '弓モ':np.array([[214,  25,  49, 235, 198, 134,   7,  18]], dtype='uint8'),
        '槍モ':np.array([[150,   9, 227,  88, 114, 153,  76,  56]], dtype='uint8'),
        '騎モ':np.array([[246,  73,   1, 153,  50,  28,  69, 242]], dtype='uint8'),
        '術モ':np.array([[150,  73,  99,  24,  51,   6,  76, 145]], dtype='uint8'),
        '殺モ':np.array([[ 6,  99, 177,  24, 194, 179,  69,  28]], dtype='uint8'),
        '狂モ':np.array([[ 54,  73, 193,  32,  39, 145,  73, 155]], dtype='uint8'),
        '剣ピ':np.array([[150, 41, 99, 152, 75, 141, 204, 18]], dtype='uint8'),
        '弓ピ':np.array([[150, 120,  53, 203, 194, 150, 135,  18]], dtype='uint8'),
        '槍ピ':np.array([[150,  41, 227,  88, 114, 153, 204,  56]], dtype='uint8'),
        '騎ピ':np.array([[246,  73,  49, 153, 114,  28, 197, 242]], dtype='uint8'),
        '術ピ':np.array([[150, 201,  51,  24, 226,  36, 204, 145]], dtype='uint8'),
        '殺ピ':np.array([[6, 105, 177,  24, 210, 179, 100,  28]], dtype='uint8'),
        '狂ピ':np.array([[54,  73, 193,  32,  98, 145,  73, 159]], dtype='uint8'),
        '未ドロップ1':np.array( [[25, 204, 50, 156, 205, 102, 167, 153]], dtype='uint8'),
        '未ドロップ2':np.array( [[152, 102,  51, 158,  77, 102, 230, 153]], dtype='uint8'),
    }

    #魔石を見分けるハッシュ値
    dist_maseki = {
        '剣魔':np.array([[153, 218, 134, 103, 122, 231, 158, 235]], dtype='uint8'),
        '弓魔':np.array([[227, 242, 24, 254, 141, 255, 230, 189]], dtype='uint8'),
        '槍魔':np.array([[131, 2, 60, 252, 248, 181, 106, 209]], dtype='uint8'),
        '騎魔':np.array([[185, 203, 118,  92,  30, 135, 247, 248]], dtype='uint8'),
        '術魔':np.array([[153, 153, 110, 227,  61,  14, 242,  58]], dtype='uint8'),
        '殺魔':np.array([[129, 166, 126, 122, 158, 123, 231, 159]], dtype='uint8'),
        '狂魔':np.array([[ 91, 166,  20,  86, 250, 123, 122, 251]], dtype='uint8'),
    }

    #輝石を見分けるハッシュ値
    dist_kiseki = {
        '剣輝':np.array([[153, 251, 142,  71, 122,  71, 158, 233]], dtype='uint8'),
        '弓輝':np.array([[227, 191,  24, 198,  29,  66, 140, 119]], dtype='uint8'),
        '槍輝':np.array([[2,  15, 230, 236, 216, 180,  44,  88]], dtype='uint8'),
        '騎輝':np.array([[185, 203, 118, 220,  30, 199, 119, 248]], dtype='uint8'),
        '術輝':np.array([[145, 153, 110,  99, 124,   6, 242,  58]], dtype='uint8'),
        '殺輝':np.array([[129, 167, 126, 123, 158, 123, 231, 159]], dtype='uint8'),
        '狂輝':np.array([[89, 167,  20,  70, 250, 123, 126, 235]], dtype='uint8'),
    }

    #種火のレアリティを見分けるハッシュ値
    dist_tanebi = {
        '全種火':np.array([[241, 88, 142, 178, 78, 205, 238, 43]], dtype='uint8'),
        '剣種火':np.array([[241, 240, 172, 186, 207, 253,  71, 172]], dtype='uint8'),
        '弓種火':np.array([[241, 240, 164, 250,  79, 253,  71, 156]], dtype='uint8'),
        '槍種火':np.array([[241, 248, 172, 186,  79, 253,  79, 172]], dtype='uint8'),
        '騎種火':np.array([[241, 112,  36, 186,  79, 253,  71, 252]], dtype='uint8'),
        '術種火':np.array([[241, 240, 164, 186,  79, 253,  71, 188]], dtype='uint8'),
        '殺種火':np.array([[241, 248, 172, 250, 207, 253, 199, 236]], dtype='uint8'),
        '狂種火':np.array([[241,  62,  46, 154, 207, 253, 230, 236]], dtype='uint8'),
        '剣灯火':np.array([[241, 220,  46, 227, 207, 153, 118, 205]], dtype='uint8'),
        '弓灯火':np.array([[241, 220,  44,  99, 207, 153, 118, 205]], dtype='uint8'),
        '槍灯火':np.array([[241, 220,  44, 227, 207, 153, 126, 205]], dtype='uint8'),
        '騎灯火':np.array([[241,  92,  46,  99, 207, 153, 118, 205]], dtype='uint8'),
        '術灯火':np.array([[251, 220, 46, 99, 207, 153, 126, 237]], dtype='uint8'),
        '殺灯火':np.array([[241, 220,  46, 227, 207, 153, 246, 205]], dtype='uint8'),
        '狂灯火':np.array([[51,  94,  14,  99, 207, 153, 246, 237]], dtype='uint8'),
        '剣大火':np.array([[179, 120,  74, 146, 244, 106,  47, 230]], dtype='uint8'),
        '弓大火':np.array([[179, 120,  74, 146, 244, 110,  47, 230]], dtype='uint8'),
        '槍大火':np.array([[179, 120,  78, 146, 244,  46,  47, 230]], dtype='uint8'),
        '騎大火':np.array([[ 51, 120,   78,  147,  247,  110,   47,  230]], dtype='uint8'),
        '術大火':np.array([[241, 220,  44,  99, 207, 153, 118, 205]], dtype='uint8'),
        '殺大火':np.array([[179, 120,  74, 146, 244, 234,  47, 230]], dtype='uint8'),
        '狂大火':np.array([[51, 120,  78, 147, 246, 232, 105, 230]], dtype='uint8'),
        '剣猛火':np.array([[43, 232, 244, 186, 159, 211, 207, 167]], dtype='uint8'),
        '弓猛火':np.array([[ 11, 232, 244, 218, 159, 215, 207, 167]], dtype='uint8'),
        '槍猛火':np.array([[11, 40, 244, 186, 190, 243, 207, 163]], dtype='uint8'),
        '騎猛火':np.array([[ 3, 104, 244,  30,  31,  87, 207, 167]], dtype='uint8'),
        '術猛火':np.array([[43, 232, 244, 154, 159, 211, 207, 167]], dtype='uint8'),
        '殺猛火':np.array([[11, 104, 244, 218, 223, 211, 207, 165]], dtype='uint8'),
        '狂猛火':np.array([[11,   8, 116,  30, 159, 211, 207, 224]], dtype='uint8'),
        '剣業火':np.array([[169, 47, 126, 248, 39, 222, 123, 182]], dtype='uint8'),
        '弓業火':np.array([[169,   47,  254,  248,   39,   94,  115,  134]], dtype='uint8'),
        '槍業火':np.array([[65,  47, 254, 216,  47,  94,  91, 182]], dtype='uint8'),
    ##    '騎業火':np.array(None,dtype='uint8'),
        '術業火':np.array([[33, 175, 254, 248, 47,94, 123, 191]], dtype='uint8'),
        '殺業火':np.array([[ 1,  47, 254, 216,  39,  94, 123, 182]], dtype='uint8'),
    ##    '狂業火':np.array([[9, 47, 174, 120, 47, 94, 243, 170]], dtype='uint8'),
    }

    #種火のクラス見分けるハッシュ値
    dist_tanebi_class = {
        '全種火':np.array([[224, 223, 56, 15, 62, 57, 7, 5]], dtype='uint8'),
        '剣種火':np.array([[152, 159, 133, 161,  48,  32, 175,  30]], dtype='uint8'),
        '弓種火':np.array([[246, 167,  25, 131, 141,   1, 234, 104]], dtype='uint8'),
        '槍種火':np.array([[194, 195, 39, 12, 104, 176, 46, 72]], dtype='uint8'),
        '騎種火':np.array([[152, 203,  54,  20, 228, 163, 103,  50]], dtype='uint8'),
        '術種火':np.array([[212, 157, 231,  98,  41, 134, 114,  26]], dtype='uint8'),
        '殺種火':np.array([[160, 167,  22,  25, 224,  41,  97, 150]], dtype='uint8'),
        '狂種火':np.array([[17, 103, 230, 222, 126, 27, 127, 217]], dtype='uint8'),
        '剣灯火':np.array([[217, 95, 167, 33, 62, 39, 14, 10]], dtype='uint8'),
        '弓灯火':np.array([[246, 135,  25, 131, 141,   1, 234, 234]], dtype='uint8'),
        '槍灯火':np.array([[226, 195, 39, 12, 104, 176,42, 73]], dtype='uint8'),
        '騎灯火':np.array([[152, 201,  54,  20, 228, 163, 103,  58]], dtype='uint8'),
        '術灯火':np.array([[212, 157, 231,  99,  41, 134, 114,  26]], dtype='uint8'),
        '殺灯火':np.array([[224, 167, 22, 25, 224, 41, 97, 150]], dtype='uint8'),
        '狂灯火':np.array([[25, 103, 230, 222, 46, 27, 123, 217]], dtype='uint8'),
        '剣大火':np.array([[216, 91, 229, 49, 58, 39, 30, 10]], dtype='uint8'),
        '弓大火':np.array([[246, 135, 137, 161, 173, 169, 234, 234]], dtype='uint8'),
        '槍大火':np.array([[226, 131,  39,  12, 104, 176,  42, 104]], dtype='uint8'),
        '騎大火':np.array([[184, 201,  54,  20, 228, 163, 119,  58]], dtype='uint8'),
        '術大火':np.array([[148, 157, 230,  98,  41, 134, 114,  58]], dtype='uint8'),
        '殺大火':np.array([[224, 166, 22, 25, 224, 57, 107, 150]], dtype='uint8'),
        '狂大火':np.array([[17, 103, 230, 222, 126, 27, 127, 217]], dtype='uint8'),
        '剣猛火':np.array([[216, 159, 213, 163, 112, 226, 125, 94]], dtype='uint8'),
        '弓猛火':np.array([[240,  39,  24, 163,  69,  41, 234, 234]], dtype='uint8'),
        '槍猛火':np.array([[192, 135,   5,  44,  88, 176,  62, 106]], dtype='uint8'),
        '騎猛火':np.array([[ 153, 233,  54,  20, 230, 163, 119,  58]], dtype='uint8'),
        '術猛火':np.array([[84, 157, 102,  99,  57, 134, 118, 58]], dtype='uint8'),
        '殺猛火':np.array([[224, 167,  86,  27, 228,  41, 101, 150]], dtype='uint8'),
        '狂猛火':np.array([[17, 103, 228, 222, 124,  27, 127, 218]], dtype='uint8'),
        '剣業火':np.array([[216, 219, 193,  33, 126,  41,  63,  10]], dtype='uint8'),
        '弓業火':np.array([[114, 191, 136,  43, 125,  42, 106,  42]], dtype='uint8'),
        '槍業火':np.array([[225, 131,   4,  44, 120, 186,  63, 106]], dtype='uint8'),
    ##    '騎業火':np.array(None, dtype='uint8'),
        '術業火':np.array([[80, 153, 199,  98,  57, 134, 118,  58]], dtype='uint8'),
        '殺業火':np.array([[169, 167, 22,  57, 224,  41,  39, 142]], dtype='uint8'),
    ##    '狂業火':np.array([[17, 103, 230, 122, 58, 27, 127, 32]], dtype='uint8'),
    }

    dist_local = {
    }


    def __init__(self):
        if not DropItems.Item_dir.is_dir():
            DropItems.Item_dir.mkdir()

        self.calc_dist_local()

    def calc_dist_local(self):
        """
        既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
        """
        files = DropItems.Item_dir.glob('**/*.png')
        for fname in files:
            img = self.imread(fname)
            DropItems.dist_local[fname] = self.compute_hash(img)

    def imread(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
        """
        OpenCVのimreadが日本語ファイル名が読めない対策
        """
        try:
            n = np.fromfile(filename, dtype)
            img = cv2.imdecode(n, flags)
            return img
        except Exception as e:
            print(e)
            return None

    def compute_hash(self, img_rgb):
        """
        判別器
        この判別器は下部のドロップ数を除いた部分を比較するもの
        記述した比率はiPpd2018画像の実測値
        """
        height, width = img_rgb.shape[:2]
    ##    img = img_rgb[int(17/135*height):int(77/135*height),
    ##                    int(19/135*width):int(103/135*width)]
        img = img_rgb[int(11/180*height):int(150/180*height),
                        int(23/166*width):int(140/166*width)]
    ##    print("通常 ",end="")
    ##    print(hasher.compute(img))
        return DropItems.hasher.compute(img)

def has_intersect(a, b):
    """
    二つの矩形の当たり判定
    """
    return max(a[0], b[0]) <= min(a[2], b[2]) \
           and max(a[1], b[1]) <= min(a[3], b[3])

class ScreenShot:
    unknown_item_count = 0

    def __init__(self, img_rgb, svm, dropitems):
        threshold = 80

        self.img_rgb = img_rgb
        self.img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        th, self.img_th = cv2.threshold(self.img_gray, threshold, 255, cv2.THRESH_BINARY)
        
        self.height, self.width = img_rgb.shape[:2]
        item_pts = []
        item_pts = self.img2points()

        self.items = []
        for pt in item_pts:
            item_img_rgb = self.img_rgb[pt[1] :  pt[3],  pt[0] :  pt[2]]
            item_img_gray = self.img_gray[pt[1] :  pt[3],  pt[0] :  pt[2]]
            item = Item(item_img_rgb, item_img_gray, svm, dropitems)
            if item.name.endswith("火"):
                break
            if item.name == "QP":
                break
            self.items.append(item)

        self.itemdic = self.makeitemdict()
        self.itemlist = self.makeitemlist()

    def makeitemdict(self):
        """
        """
        itemdic = {}
        for item in self.items:
            if item.name[-1].isdigit():
                itemdic[item.name + '_'] = item.dropnum
            else:
                itemdic[item.name] = item.dropnum                
        return itemdic

    def makeitemlist(self):
        """
        """
        itemlist = []
        for item in self.items:
            if item.name[-1].isdigit():
                itemlist.append((item.name + '_', item.dropnum))
            else:
                itemlist.append((item.name, item.dropnum))
        return itemlist

    def pattern2048x946(self):
        """
        2048x946は2パターンあるため振り分けする
        """
        lower = np.array([192,192,192]) 
        upper = np.array([250,250,250])
        img_mask = cv2.inRange(self.img_rgb, lower, upper)
        contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        item_pts = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 12000 and area < 15000:
                epsilon = 0.01*cv2.arcLength(cnt,True)
                approx = cv2.approxPolyDP(cnt,epsilon,True)
                if len(approx) >= 5:
        ##        if len(approx) > 5:
##                    cv2.drawContourss(self.img_rgb, [approx], -1, (0,0,255), 3)
                    ret = cv2.boundingRect(cnt)
                    pts = [ ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3] ]
                    item_pts.append(pts)            
        ## Y列でソート
        item_pts.sort(key=lambda x: x[1])
        if item_pts[0][0] < 249:
            return 0
        return 1
        
    def pattern2048x878(self):
        """
        2048x878は2パターンあるため振り分けする
        """
        lower = np.array([192,192,192]) 
        upper = np.array([250,250,250])
        img_mask = cv2.inRange(self.img_rgb, lower, upper)
        contours = cv2.findContours(img_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        item_pts = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 12000 and area < 15000:
                epsilon = 0.01*cv2.arcLength(cnt,True)
                approx = cv2.approxPolyDP(cnt,epsilon,True)
                if len(approx) >= 5:
        ##        if len(approx) > 5:
##                    cv2.drawContours(img_rgb, [approx], -1, (0,0,255), 3)
                    ret = cv2.boundingRect(cnt)
                    pts = [ ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3] ]
                    item_pts.append(pts)            
        ## Y列でソート
        item_pts.sort(key=lambda x: x[1])
        if item_pts[0][0] < 190:
            return 0
        return 1

    def img2points(self):
        """
        戦利品が出現する12(4x3)の座標 [left, top, right, bottom]
        解像度別に設定
        """
        if self.width == 3840 and self.height == 2160:
            pts = [(243, 784, 559, 1127), (597, 784, 911, 1127), (948, 784, 1265, 1127), (1301, 784, 1616, 1127),
                   (243, 1145, 559, 1489), (597, 1145, 911, 1489), (948, 1145, 1265, 1489),(1301, 1145, 1616, 1489),
                   (243, 1505, 559, 1848), (597, 1505, 911, 1848), (948, 1505, 1265, 1848), (1301, 1505, 1616, 1848)]            
        elif self.width == 2880 and self.height == 1440:
            pts = [(323, 525, 532, 751), (558, 525, 767, 751), (793, 525, 1002, 751), (1028, 525, 1237, 751),
                   (323, 765, 532, 991), (558, 765, 767, 991), (793, 765, 1002, 991),(1028, 765, 1237, 991),
                   (323, 1005, 532, 1258), (558, 1005, 767, 1258), (793, 1005, 1002, 1258), (1028, 1005, 1237, 1258)]            
        elif self.width == 2224 and self.height == 1668:
            pts = [(142, 664, 323, 862), (346, 664, 527, 862), (550, 664, 731, 862), (754, 664, 935, 862),
                   (142, 872, 323, 1070), (346, 872, 527, 1070), (550, 872, 731, 1070),(754, 872, 935, 1070),
                   (142, 1080, 323, 1278), (346, 1080, 527, 1278), (550, 1080, 731, 1278), (754, 1080, 935, 1278)]
        elif self.width == 2048 and (self.height == 1535 or self.height == 1536):
            pts = [(131, 612, 297, 792), (319, 612, 485, 792), (507, 612, 673, 792), (695, 612, 861, 792),
                   (131, 804, 297, 984), (319, 804, 485, 984), (507, 804, 673, 984),(695, 804, 861, 984),
                   (131, 996, 297, 1176), (319, 996, 485, 1176), (507, 996, 673, 1176), (695, 996, 861, 1176)]
        elif self.width == 2048 and (self.height == 1431 or self.height == 1430):
            pts = [(131, 557, 297, 741), (319, 557, 485, 741), (507, 557, 673, 741), (695, 557, 861, 741),
                   (131, 749, 297, 933), (319, 749, 485, 933), (507, 749, 673, 933), (695, 749, 861, 933),
                   (131, 941, 297, 1125), (319, 941, 485, 1125), (507, 941, 673, 1125), (695, 941, 861, 1125)]
        elif (self.width == 2048 or self.width == 2047) and (self.height == 1151 or self.height == 1152): 
            pts = [(131, 419, 297, 601), (319, 419, 485, 601), (507, 419, 673, 601), (695, 419, 861, 601),
                   (131, 612, 297, 794), (319, 612, 485, 794), (507, 612, 673, 794), (695, 612, 861, 794),
                   (131, 802, 297, 986), (319, 802, 485, 986), (507, 802, 673, 986), (695, 802, 861, 986)]
##        elif self.width == 2048 and self.height == 1152: 
##            pts = [(131, 419, 297, 601), (319, 419, 485, 601), (507, 419, 673, 601), (695, 419, 861, 601),
##                   (131, 612, 297, 794), (319, 612, 485, 794), (507, 612, 673, 794), (695, 612, 861, 794),
##                   (131, 802, 297, 986), (319, 802, 485, 986), (507, 802, 673, 986), (695, 802, 861, 986)]
        elif self.width == 2048 and (self.height == 1145 or self.height == 1144 or self.height == 1143): 
            pts = [(131, 412, 297, 595), (319, 412, 485, 595), (507, 412, 673, 595), (695, 412, 861, 595),
                   (131, 605, 297, 789), (319, 605, 485, 789), (507, 605, 673, 789), (695, 605, 861, 789),
                   (131, 799, 297, 882), (319, 799, 485, 882), (507, 799, 673, 882), (695, 799, 861, 882)]
        elif self.width == 2048 and self.height == 1024: 
            pts = [(230, 373, 378, 534), (396, 373, 545, 534), (564, 373, 712, 534), (731, 373, 879, 534),
                   (230, 543, 378, 706), (396, 543, 545, 706), (564, 543, 712, 706), (731, 543, 879, 706),
                   (230, 715, 378, 876), (396, 715, 545, 876), (564, 715, 712, 876), (731, 715, 879, 876)]

        elif self.width == 2048 and self.height == 996:
            pts = [(251, 361, 396, 521), (414, 361, 558, 521), (576, 361, 722, 521), (739, 361, 883, 521),
                   (251, 527, 396, 686), (414, 527, 558, 686), (576, 527, 722, 686), (739, 527, 883, 686),
                   (251, 694, 396, 852), (414, 694, 558, 852), (576, 694, 722, 852), (739, 694, 883, 852)]
##        elif self.width == 2048 and self.height == 970:
##            pts = [(325, 352, 466, 506), (484, 352, 624, 506), (642, 352, 783, 506), (800, 352, 941, 506),
##                   (325, 514, 466, 669), (484, 514, 624, 669), (642, 514, 783, 669), (800, 514, 941, 669),
##                   (325, 676, 466, 830), (484, 676, 624, 830), (642, 676, 783, 830), (800, 676, 941, 830)]
        elif self.width == 2048 and self.height == 970:
            pts = [(322, 352, 463, 506), (480, 352, 621, 506), (638, 352, 779, 506), (796, 352, 937, 506),
                   (322, 514, 463, 669), (480, 514, 621, 669), (638, 514, 779, 669), (796, 514, 937, 669),
                   (322, 676, 463, 830), (480, 676, 621, 830), (638, 676, 779, 830), (796, 676, 937, 830)]
        elif self.width == 2048 and self.height == 946: # iOS系?同じ解像度で位置が二つある？
            if self.pattern2048x946() == 0:
                pts = [(327, 327, 458, 469), (474, 327, 604, 469), (620, 327, 752, 469), (767, 327, 897, 469),
                       (327, 477, 458, 619), (474, 477, 604, 619), (620, 477, 752, 619), (767, 477, 897, 619),
                       (327, 627, 458, 769), (474, 627, 604, 769), (620, 627, 752, 769), (767, 627, 897, 769)]
            else:
                pts = [(332, 325, 461, 467), (477, 325, 608, 467), (623, 325, 752, 467), (769, 325, 898, 467),
                       (332, 474, 461, 616), (477, 474, 608, 616), (623, 474, 752, 616), (769, 474, 898, 616),
                       (332, 623, 461, 763), (477, 623, 608, 763), (623, 623, 752, 763), (769, 623, 898, 763)]
        elif self.width == 2048 and self.height == 878:
            if self.pattern2048x878() == 0:
                pts = [(241, 320, 368, 458), (384, 320, 513, 458), (526, 320, 655, 458), (670, 320, 799, 458),
                       (241, 465, 368, 603), (384, 465, 513, 603), (526, 465, 655, 603), (670, 465, 799, 603),
                       (241, 611, 368, 749), (384, 611, 513, 749), (526, 611, 655, 749), (670, 611, 799, 749)]
            else:
                pts = [(292, 320, 419, 458), (435, 320, 563, 458), (577, 320, 707, 458), (722, 320, 849, 458),
                       (292, 465, 419, 603), (435, 465, 563, 603), (577, 465, 707, 603), (722, 465, 849, 603),
                       (292, 611, 419, 749), (435, 611, 563, 749), (577, 611, 707, 749), (722, 611, 849, 749)]
        elif self.width == 2031 and self.height == 1144: 
            pts = [(130, 414, 298, 597), (317, 414, 486, 597), (506, 414, 675, 597), (694, 414, 862, 597),
                   (130, 605, 298, 790), (317, 605, 486, 790), (506, 605, 675, 790), (694, 605, 862, 790),
                   (130, 797, 298, 981), (317, 797, 486, 981), (506, 797, 675, 981), (694, 797, 862, 981)]
        elif self.width == 1920 and self.height == 1200: #次はここ
            pts = [(123, 453, 279, 623), (299, 453, 455, 623), (475, 453, 631, 623), (651, 453, 807, 623),
                   (123, 633, 279, 803), (299, 633, 455, 803), (475, 633, 631, 803), (651, 633, 807, 803),
                   (123, 813, 279, 983), (299, 813, 455, 983), (475, 813, 631, 983), (651, 813, 807, 983)]

        elif self.width == 1918 and self.height == 1080: #次はここ
            pts = [(121, 392, 278, 564), (298, 392, 454, 564), (474, 392, 630, 564), (650, 392, 807, 564),
                   (121, 572, 278, 744), (298, 572, 454, 744), (474, 572, 630, 744), (650, 572, 807, 744),
                   (121, 752, 278, 923), (298, 752, 454, 923), (474, 752, 630, 923), (650, 752, 807, 923)]
        elif self.width == 1885 and self.height == 1059: #次はここ
            pts = [(123, 387, 276, 554), (296, 387, 449, 554), (468, 387, 623, 554), (642, 387, 796, 554),
                   (123, 562, 276, 731), (299, 562, 449, 731), (468, 562, 623, 731), (642, 562, 796, 731),
                   (123, 739, 276, 908), (299, 739, 449, 908), (468, 739, 623, 908), (642, 739, 796, 908)]
        elif self.width == 1884 and self.height == 870: #次はここ
            pts = [(304, 299, 425, 430), (438, 299, 558, 430), (573, 299, 693, 430), (707, 299, 826, 430),
                   (304, 435, 425, 567), (438, 435, 558, 567), (573, 435, 693, 567), (707, 435, 826, 567),
                   (304, 456, 425, 704), (438, 456, 558, 704), (573, 456, 693, 704), (707, 456, 826, 704)]
        elif self.width == 1792 and self.height == 828: #次はここ
            pts = [(285, 285, 400, 411), (414, 285, 529, 411), (542, 285, 658, 411), (670, 285, 786, 411),
                   (285, 416, 400, 542), (414, 416, 529, 542), (542, 416, 658, 542), (670, 416, 786, 542),
                   (285, 547, 400, 673), (414, 547, 529, 673), (542, 547, 658, 673), (670, 547, 786, 673)]
        elif self.width == 1707 and self.height == 960: #次はここ
            pts = [(108, 349, 249, 502), (266, 349, 405, 502), (422, 349, 562, 502), (579, 349, 719, 502),
                   (108, 508, 249, 661), (266, 508, 405, 661), (422, 508, 562, 661), (579, 508, 719, 661),
                   (108, 667, 249, 830), (266, 667, 405, 830), (422, 667, 562, 830), (579, 667, 719, 830)]
        elif self.width == 1624 and self.height == 750: #次はここ
            pts = [(263, 258, 365, 369), (379, 258, 481, 369), (494, 258, 598, 369), (610, 258, 712, 369),
                   (263, 376, 365, 488), (379, 376, 481, 488), (494, 376, 598, 488), (610, 376, 712, 488),
                   (263, 494, 365, 606), (379, 494, 481, 606), (494, 494, 598, 606), (610, 494, 712, 606)]
##        elif self.width == 1397 and self.height == 786:
##            pts = [(89, 285, 203, 411), (218, 285, 332, 411), (346, 285, 460, 411), (474, 285, 588, 411),
##                       (89, 416, 203, 545), (218, 416, 332, 545), (346, 416, 460, 545), (474, 416, 588, 545),
##                       (89, 547, 203, 673), (218, 547, 332, 673), (346, 547, 460, 673), (474, 547, 588, 673)]
        elif self.width == 1392 and self.height == 783:
            pts = [(89, 285, 202, 410), (216, 285, 330, 410), (344, 285, 458, 410), (472, 285, 586, 410),
                       (89, 415, 202, 540), (216, 415, 330, 540), (344, 415, 458, 540), (472, 415, 586, 540),
                       (89, 546, 202, 671), (216, 546, 330, 671), (344, 546, 458, 671), (472, 546, 586, 671)]
        elif self.width == 1391 and self.height == 786:
            pts = [(81, 285, 197, 411), (209, 285, 325, 411), (337, 285, 453, 411), (465, 285, 581, 411),
                       (81, 416, 197, 542), (209, 416, 325, 542), (337, 416, 453, 542), (465, 416, 581, 542),
                       (81, 547, 197, 673), (209, 547, 325, 673), (337, 547, 453, 673), (465, 547, 581, 673)]
        elif self.width == 1334 and self.height == 750: #そしてここ
            pts = [(85, 273, 194, 392), (207, 273, 316, 392), (330, 273, 439, 392), (452, 273, 561, 392),
                       (85, 398, 194, 517), (207, 398, 316, 517), (330, 398, 439, 517), (452, 398, 561, 517),
                       (85, 523, 194, 642), (207, 523, 316, 642), (330, 523, 439, 642), (452, 523, 561, 642)]
        elif self.width == 1333 and self.height == 749: #そしてここ
            pts = [(118, 257, 221, 370), (234, 257, 336, 370), (349, 257, 452, 370), (465, 257, 567, 370),
                       (118, 375, 221, 487), (234, 375, 336, 487), (349, 375, 452, 487), (465, 375, 567, 487),
                       (118, 492, 221, 604), (234, 492, 336, 604), (349, 492, 452, 604), (465, 492, 567, 604)]
        elif self.width == 1280 and self.height == 800: #そしてここ
            pts = [(82, 301, 186, 417), (199, 301, 303, 417), (317, 301, 421, 417), (434, 301, 538, 417),
                       (82, 421, 186, 536), (199, 421, 303, 536), (317, 421, 421, 536), (434, 421, 538, 536),
                       (82, 541, 186, 656), (199, 541, 303, 656), (317, 541, 421, 656), (434, 541, 538, 656)]
        elif self.width == 1280 and self.height == 720: #そしてここ
            pts = [(82, 262, 186, 377), (199, 262, 303, 377), (317, 262, 421, 377), (434, 262, 538, 377),
                       (82, 382, 186, 496), (199, 382, 303, 496), (317, 382, 421, 496), (434, 382, 538, 496),
                       (82, 502, 186, 616), (199, 502, 303, 616), (317, 502, 421, 616), (434, 502, 538, 616)]
        elif self.width == 1136 and self.height == 640: #そしてここ
            pts = [(71, 233, 164, 335), (175, 233, 269, 335), (280, 233, 373, 335), (384, 233, 478, 335),
                       (71, 339, 164, 441), (175, 339, 269, 441), (280, 339, 373, 441), (384, 339, 478, 441),
                       (71, 446, 164, 548), (175, 446, 269, 548), (280, 446, 373, 548), (384, 446, 478, 548)]
        elif self.width == 1024 and self.height == 768: 
            pts = [(64, 306, 150, 396), (158, 306, 243, 396), (253, 306, 338, 396), (347, 306, 432, 396),
                       (64, 402, 150, 493), (158, 402, 243, 493), (253, 402, 338, 493), (347, 402, 432, 493),
                       (64, 501, 150, 591), (158, 501, 243, 591), (253, 501, 338, 591), (347, 501, 432, 591)]
        elif self.width == 1024 and self.height == 576: 
            pts = [(64, 209, 150, 301), (158, 209, 243, 301), (253, 209, 338, 301), (347, 209, 432, 301),
                       (64, 304, 150, 397), (158, 304, 243, 397), (253, 304, 338, 397), (347, 304, 432, 397),
                       (64, 401, 150, 494), (158, 401, 243, 494), (253, 401, 338, 494), (347, 401, 432, 494)]
        else:
            print(str(self.width) + 'x' + str(self.height) +  ":未対応")
            pts = []

        return pts

class Item:
    hasher = cv2.img_hash.PHash_create()
    def __init__(self, img_rgb, img_gray, svm, dropitems):
        self.img_rgb = img_rgb
        self.img_gray = img_gray
        self.img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.height, self.width = img_rgb.shape[:2]
        self.svm = svm
        self.dropitems = dropitems
        self.dropnum = self.ocr_digit()
        self.name = self.classify_item(img_rgb)

    def conflictcheck(self, pts, pt):
        """
        pt が ptsのどれかと衝突していたら面積に応じて入れ替える
        """
        flag = False
        for p in list(pts):
            if has_intersect(p, pt) == True:
            # どちらかを消す
                p_area = (p[2]-p[0])*(p[3]-p[1])
                pt_area = (pt[2]-pt[0])*(pt[3]-pt[1])
                if p_area > pt_area:
                    pts.remove(p)                        
                else:
                    flag = True

        if flag == False:
            pts.append(pt)
        return pts

    def detect_char(self):
        """
        戦利品数OCRで銀枠を除く(Reward QPは含む)下段の白文字の座標を抽出する

        ノイズは少し気になる程度
        """
        h, w = self.img_hsv.shape[:2]
        digitimg = self.img2digitimg(self.img_hsv)
        return digitimg

    def is_silver_item(self):
        silver_list = [    '種', 'ランタン', '八連', '宝玉', '羽根', '歯車', '頁', 'ホム',
                        '蹄鉄', '勲章', '貝殻', '勾玉', '結氷', '指輪', 'オーロラ', '鈴',
                        '矢尻', '冠',
                        '剣魔', '弓魔', '槍魔', '騎魔', '術魔', '殺魔', '狂魔',
                        '剣ピ', '弓ピ', '槍ピ', '騎ピ', '術ピ', '殺ピ', '狂ピ',
                    ]
        if self.name in silver_list:
            return True
        return False
            
    def ocr_digit(self):
        """
        戦利品OCR
        """
        pts = [
            (int(64/166*self.width), int(151/180*self.height),
               int(87/166*self.width), int(176/180*self.height)),

            (int(82/166*self.width), int(151/180*self.height),
               int(103/166*self.width), int(176/180*self.height)),
               


            (int(105/166*self.width), int(151/180*self.height),
               int(125/166*self.width), int(176/180*self.height)),
               
                (int(123/166*self.width), int(151/180*self.height),
               int(143/166*self.width), int(176/180*self.height)),
               
                (int(140/166*self.width), int(151/180*self.height),
               int(159/166*self.width), int(176/180*self.height)),
               ]
        line_lower_white = self.read_item(self.img_gray, pts)

        return line_lower_white

    def img2digitimg(self, img_hsv, im_th):
        """
        白でマスク(文字のフチのみ白に)→2値化画像とOR(文字内部のみ黒に)→
        白エリア収縮することで文字(黒)拡張→反転(文字内部のみ白に)
        """
        lower_white = np.array([0,1, 0]) 
        upper_white = np.array([255,255, 255])
        img_hsv_mask = cv2.inRange(img_hsv, lower_white, upper_white)
        kernel = np.ones((2,2),np.uint8)
        img = cv2.cv2.bitwise_or(img_hsv_mask, im_th)
        erosion = cv2.erode(img,kernel,iterations = 1)
        erosion_rev = cv2.cv2.bitwise_not(erosion)

        return erosion_rev

    def classify_standard_item(self, img):
        """
        imgとの距離を比較して近いアイテムを求める
        """
        # 種火かどうかの判別
        hash_tanebi = self.compute_tanebi_hash(img)
        tanebifiles = {}
        for i in self.dropitems.dist_tanebi.keys():
            dt = Item.hasher.compare(hash_tanebi, self.dropitems.dist_tanebi[i])
            if dt <= 15: #IMG_1833で11 IMG_1837で15
                tanebifiles[i] = dt
        tanebifiles = sorted(tanebifiles.items(), key=lambda x:x[1])

        if len(tanebifiles) > 0:
            return "種火"
        
        hash_item = self.compute_hash(img) #画像の距離
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in self.dropitems.dist_item.keys():
            d = Item.hasher.compare(hash_item, self.dropitems.dist_item[i])
            if d <= 15:
            #ポイントと種の距離が8という例有り(IMG_0274)→16に
            #バーガーと脂の距離が10という例有り(IMG_2354)→14に
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x:x[1])
            item = next(iter(itemfiles))
            if item[0].endswith("魔"):
                hash_ma = self.compute_maseki_hash(img)
                masekifiles = {}
                for i in self.dropitems.dist_maseki.keys():
                    d2 = Item.hasher.compare(hash_ma, self.dropitems.dist_maseki[i])
                    if d2 <= 24:
                        masekifiles[i] = d2
                masekifiles = sorted(masekifiles.items(), key=lambda x:x[1])
                try:
                    item = next(iter(masekifiles))
                except:
                    return ""
            elif item[0].endswith("輝"):
                hash_ki = self.compute_maseki_hash(img)
                kisekifiles = {}
                for i in self.dropitems.dist_kiseki.keys():
                    d2 = Item.hasher.compare(hash_ki, self.dropitems.dist_kiseki[i])
                    if d2 <= 20:
                        kisekifiles[i] = d2
                kisekifiles = sorted(kisekifiles.items(), key=lambda x:x[1])
                try:
                    item = next(iter(kisekifiles))
                except:
                    return ""
            elif item[0].endswith("モ") or item[0].endswith("ピ"):
                #ヒストグラム
                img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                h, w = img_hsv.shape[:2]
                img_hsv = img_hsv[int(h/2-10):int(h/2+10),int(w/2-10):int(w/2+10)]
                hist_s = cv2.calcHist([img_hsv],[1],None,[256],[0,256]) #Bのヒストグラムを計算
                minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist_s)
                if maxLoc[1] > 128:
                    return item[0][0] + "モ"
                else:
                    return item[0][0] + "ピ"
                
            return item[0]

        return ""

    def classify_local_item(self, img):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = self.compute_hash(img) #画像の距離

        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in self.dropitems.dist_local.keys():
            d = Item.hasher.compare(hash_item, self.dropitems.dist_local[i])
            #同じアイテムでも14離れることあり(IMG_8785)
            if d <= 15:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x:x[1])
            item = next(iter(itemfiles))
            if isinstance(item[0], str):
                return item[0]
            return item[0].stem

        return ""

    def make_new_file(self, img):
        """
        ファイル名候補を探す
        """
        if self.dropnum == "":
            ScreenShot.unknown_item_count = ScreenShot.unknown_item_count + 1
            itemname = "泥無しアイテム" + str(ScreenShot.unknown_item_count)
            self.dropitems.dist_local[itemname] = self.compute_hash(img)
            return itemname
        for i in range(99999):
            itemfile = self.dropitems.Item_dir / ('item{:0=6}'.format(i + 1) + '.png')
            if itemfile.is_file():
                continue
            else:
                img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cv2.imwrite(itemfile.as_posix(), img_gray)
                self.dropitems.dist_local[itemfile] = self.compute_hash(img)
                break
        return itemfile.stem

    def make_new_file2(self, img):
        """
        ファイル名候補を探す
        """
        for i in range(99999):
            itemfile = self.dropitems.Item_dir / ('item{:0=6}'.format(i + 1) + '.png')
            if itemfile.is_file():
                continue
            else:
                cv2.imwrite(itemfile.as_posix(), img)
                self.dropitems.dist_local[itemfile] = self.compute_hash(img)
                break
        return itemfile.stem

    def make_new_item(self, img):
        """
        アイテム名候補を探す
        """
        for i in range(58):
            itemname = (chr(i+65) + '泥')
            if itemname in self.dropitems.dist_local.keys():
                continue
            else:
                dist_local[itemname] = self.compute_hash(img)
                break
        return itemname

    def classify_item(self, img):
        """
        アイテム判別器
        """
        item = self.classify_standard_item(img)
        if item == "":
            item = self.classify_local_item(img)
        if item == "":
            item = self.make_new_file(img)
        return item

    def compute_tanebi_hash(self, img_rgb):
        """
        種火レアリティ判別器
        この場合は画像全域のハッシュをとる
        """
        return Item.hasher.compute(img_rgb)

    def compute_tanebi_class_hash(self, img_rgb):
        """
        種火クラス判別器
        左上のクラスマークぎりぎりのハッシュを取る
        記述した比率はiPhone6S画像の実測値
        """
        img = img_rgb[int(5/135*self.height):int(30/135*self.height),
                      int(5/135*self.width):int(30/135*self.width)]

        return Item.hasher.compute(img)

    def compute_maseki_hash(self, img_rgb):
        """
        魔石クラス判別器
        中央のクラスマークぎりぎりのハッシュを取る
        記述した比率はiPhone6S画像の実測値
        """
        img = img_rgb[int(41/135*self.height):int(84/135*self.height),
                      int(44/124*self.width):int(79/124*self.width)]
        return Item.hasher.compute(img)


    def read_item(self, img_gray, pts, upper=False, yellow=False,):
        """
        戦利品の数値をOCRする(エラー訂正有)
        """
        width = img_gray.shape[1]

        win_size = (120, 60)
        block_size = (16, 16)
        block_stride = (4, 4)
        cell_size = (4, 4)
        bins = 9

        lines = ""
        for pt in reversed(pts):
            char = []
            tmpimg = img_gray[pt[1]:pt[3], pt[0]:pt[2]]
##            cv2.imshow("img", tmpimg)
##            cv2.waitKey(0)
##            cv2.destroyAllWindows()
##            self.make_new_file2(tmpimg)
            tmpimg = cv2.resize(tmpimg, (win_size))
            hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, bins)
            char.append(hog.compute(tmpimg))
            char = np.array(char)
            pred = self.svm.predict(char)
            result = int(pred[1][0][0])
            if int(pred[1][0][0]) == 0:
                break
            lines = lines + chr(result)


        return lines[::-1]

    def compute_hash(self, img_rgb):
        """
        判別器
        この判別器は下部のドロップ数を除いた部分を比較するもの
        記述した比率はiPpd2018画像の実測値
        """
        height, width = img_rgb.shape[:2]
        img = img_rgb[int(11/180*height):int(150/180*height),
                        int(23/166*width):int(140/166*width)]
        return Item.hasher.compute(img)


def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    """
    OpenCVのimreadが日本語ファイル名が読めない対策
    """
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None
        
if __name__ == '__main__':
    dropitems = DropItems()        
    svm = cv2.ml.SVM_load(str(training))
    file = Path(sys.argv[1])
    img_rgb = imread(str(file))
    sc = ScreenShot(img_rgb, svm, dropitems)
    result = ""
    for item in sc.itemlist:
        if not item[0].startswith("未ドロップ"):
            result = result + item[0] + item[1] + '-'
    if len(result) > 0:
        print(result[:-1])
