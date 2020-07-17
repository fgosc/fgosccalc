#!/usr/bin/env python3
import sys
import cv2
from pathlib import Path
import numpy as np
import argparse
from storage.filesystem import FileSystemStorage
import csv
import re

progname = "img2str"
version = "0.2.0"

training = Path(__file__).resolve().parent / Path("property.xml") #アイテム下部
defaultItemStorage = FileSystemStorage(Path(__file__).resolve().parent / Path("item/"))
Item_dist_file = Path(__file__).resolve().parent / Path("hash_item.csv")
CE_dist_file = Path(__file__).resolve().parent / Path("hash_ce.csv")


class DropItems:
    hasher = cv2.img_hash.PHash_create()


    #恒常アイテムのハッシュ値
    dist_item ={
##        'QP':np.array([[214,  27,  77, 212,  33, 165,  72, 134]], dtype='uint8'),
##        '爪':np.array([[250,  14, 161,  65,  22, 225, 125,  12]], dtype='uint8'),
##        '心臓':np.array([[246,  14,  39, 163,  41, 179,  24,   9]], dtype='uint8'),
##        '逆鱗':np.array([[ 30,  14, 225, 248,  33, 145, 135,  17]], dtype='uint8'),
##        '根':np.array([[30, 67, 225, 44, 27, 89, 134, 148]], dtype='uint8'),
##        '幼角':np.array([[30,  99, 233,  94,  51, 141,  22, 147]], dtype='uint8'),
##        '涙石':np.array([[54,  97,  73,  24, 135,   4,  73,  20]], dtype='uint8'),
##        '脂':np.array([[ 86,  44,   5,   3,   1,  89, 227,   2]], dtype='uint8'),
##        'ランプ':np.array([[102,  41, 143, 153, 148,  99,  52,  88]], dtype='uint8'),
##        'スカラベ':np.array([[36, 47, 157, 70, 3, 80, 99, 48]], dtype='uint8'),
##        '産毛':np.array([[ 92, 163,  71,  24,  91, 173, 133, 100]], dtype='uint8'),
##        '胆石':np.array([[214,  19, 129,  76,  35, 138, 188,  81]], dtype='uint8'),
##        '神酒':np.array([[118,  25,  20, 108, 227, 129,  81, 155]], dtype='uint8'),
##        '炉心':np.array([[70,  51, 141,  28,  11,  39,  89, 140]], dtype='uint8'),
##        '鏡':np.array([[ 22,  75, 181,  92,  20,  83, 138,   4]], dtype='uint8'),
##        '卵':np.array([[54,  50,  33,  12,  73, 197,  17,  97]], dtype='uint8'),
##        'カケラ':np.array([[118, 163,   5,  12, 233, 148,  73,  38]], dtype='uint8'),
##        '実':np.array([[ 84, 187,   1,  86,  67, 164, 157,  14]], dtype='uint8'),
##        '種':np.array([[126, 33, 5, 120, 161, 94, 81, 20]], dtype='uint8'),
##        'ランタン':np.array([[166, 152, 137,  89, 146,  17, 164, 196]], dtype='uint8'),
##        '八連':np.array([[206,  81,  61, 174, 129,  26,  97,  22]], dtype='uint8'),
##        '宝玉':np.array([[92,  72, 141, 151, 194, 225, 176, 167]], dtype='uint8'),
##        '羽根':np.array([[62, 162, 161, 221, 28, 73, 105, 101]], dtype='uint8'),
##        '歯車':np.array([[60, 222, 7, 1, 225, 113, 121, 165]], dtype='uint8'),
##        '頁':np.array([[23,  56, 175, 194, 236, 115, 102, 236]], dtype='uint8'),
##        'ホム':np.array([[214,   1,   3,  88,  12, 132, 163, 114]], dtype='uint8'),
##        '蹄鉄':np.array([[248, 137,  23,  82, 163, 180, 123,  60]], dtype='uint8'),
##        '勲章':np.array([[182,  18,  90, 232,   9, 173, 165,  37]], dtype='uint8'),
##        '貝殻':np.array([[122, 106, 165, 149, 201, 72, 27, 148]], dtype='uint8'),
##        '勾玉':np.array([[25, 20, 255, 234, 4, 27, 216, 166]], dtype='uint8'),
##        '結氷':np.array([[94,  67,  29, 232, 196,  28, 179, 206]], dtype='uint8'),
##        '指輪':np.array([[218, 225,   7,   9,   5,  98, 137, 115]], dtype='uint8'),
##        'オーロラ':np.array([[92,   3, 233, 148,  92,  37, 153,  33]], dtype='uint8'),
##        '鈴':np.array([[202,  67,  29,  32,  19,  44,  17, 202]], dtype='uint8'),
##        '矢尻':np.array([[244,  47, 139,  64,  43,  41, 218, 217]], dtype='uint8'),
##        '冠':np.array([[47, 168, 253, 102, 137, 252, 114, 169]], dtype='uint8'),
##        '霊子':np.array([[194, 134,  87, 232, 169, 121,  43,  83]], dtype='uint8'),
##        '証':np.array([[86, 7, 5, 1, 97, 88, 14, 6]], dtype='uint8'),
##        '骨':np.array([[90,  83,  88,  77, 101, 149, 213,  81]], dtype='uint8'),
##        '牙':np.array([[82,  83,   4, 181,  17,  25, 141, 241]], dtype='uint8'),
##        '塵':np.array([[28, 5, 5, 64, 89, 92, 5, 4]], dtype='uint8'),
##        '鎖':np.array([[254,  15,   1,  33,  49, 208,   9,  45]], dtype='uint8'),
##        '毒針':np.array([[82, 181, 165, 105,  75,  91,  19, 179]], dtype='uint8'),
##        '髄液':np.array([[ 54, 105, 211, 166,  76,  27,  44,  24]], dtype='uint8'),
##        '鉄杭':np.array([[ 28,  29,  56,  51,  99, 131,   3,   7]], dtype='uint8'),
##        '火薬':np.array([[90, 167,  17,  41,  48,  29, 141, 225]], dtype='uint8'),
##        '剣秘':np.array([[232, 26, 150, 166, 67, 123, 119, 168]], dtype='uint8'),
##        '弓秘':np.array([[232,  30, 118, 130,   7, 115, 101, 152]], dtype='uint8'),
##        '槍秘':np.array([[232,  30, 214, 179,  71, 220, 189,  96]], dtype='uint8'),
##        '騎秘':np.array([[226,  26, 158, 166,  71, 121, 247, 184]], dtype='uint8'),
##        '術秘':np.array([[232, 22, 94, 137, 71, 118, 125, 200]], dtype='uint8'),
##        '殺秘':np.array([[232,  26, 150, 102,  70, 187, 121, 232]], dtype='uint8'),
##        '狂秘':np.array([[232,  26,  86, 102,   6,  59, 117, 136]], dtype='uint8'),
##        '剣魔':np.array([[86, 131, 165, 241, 161, 24, 9, 28]], dtype='uint8'),
##        '弓魔':np.array([[86,   3, 133, 225,  33,  24,  25,  28]], dtype='uint8'),
##        '槍魔':np.array([[94, 131, 133, 233, 161, 48, 41, 28]], dtype='uint8'),
##        '騎魔':np.array([[94,   3, 165, 225, 169,  80,   9,  28]], dtype='uint8'),
##        '術魔':np.array([[94,   3, 165, 241, 169,  88,  41,  24]], dtype='uint8'),
##        '殺魔':np.array([[86,   3, 165, 241, 169, 120,   9,  24]], dtype='uint8'),
##        '狂魔':np.array([[86,   3, 133, 177, 169,  88,   9,  28]], dtype='uint8'),
##        '剣輝':np.array([[30, 3, 5, 41, 105, 18, 81, 4]], dtype='uint8'),
###        '弓輝':np.array([[118,  67, 133,  41, 105,  18,  16,   4]], dtype='uint8'),
##        '弓輝':np.array([[118,  3, 129,  41, 121,  82,  16,   4]], dtype='uint8'),
##        '槍輝':np.array([[118,  67,   5,  41, 121,  82,  73, 148]], dtype='uint8'),
##        '騎輝':np.array([[94,  67,   5,  41, 233,  82,  25, 132]], dtype='uint8'),
##        '術輝':np.array([[126,   3, 135,  33, 105,  90,  81,  20]], dtype='uint8'),
##        '殺輝':np.array([[126,  67,   5, 185, 121,  82,  16, 148]], dtype='uint8'),
##        '狂輝':np.array([[126,  71,   5, 185, 105,  82,  24,   4]], dtype='uint8'),
##        '剣モ':np.array([[22, 41, 227, 152, 75, 140, 204, 18]], dtype='uint8'),
##        '弓モ':np.array([[214,  25,  49, 235, 198, 134,   7,  18]], dtype='uint8'),
##        '槍モ':np.array([[150,   9, 227,  88, 114, 153,  76,  56]], dtype='uint8'),
##        '騎モ':np.array([[246,  73,   1, 153,  50,  28,  69, 242]], dtype='uint8'),
##        '術モ':np.array([[150,  73,  99,  24,  51,   6,  76, 145]], dtype='uint8'),
##        '殺モ':np.array([[ 6,  99, 177,  24, 194, 179,  69,  28]], dtype='uint8'),
##        '狂モ':np.array([[ 54,  73, 193,  32,  39, 145,  73, 155]], dtype='uint8'),
##        '剣ピ':np.array([[150, 41, 99, 152, 75, 141, 204, 18]], dtype='uint8'),
##        '弓ピ':np.array([[150, 120,  53, 203, 194, 150, 135,  18]], dtype='uint8'),
##        '槍ピ':np.array([[150,  41, 227,  88, 114, 153, 204,  56]], dtype='uint8'),
##        '騎ピ':np.array([[246,  73,  49, 153, 114,  28, 197, 242]], dtype='uint8'),
##        '術ピ':np.array([[150, 201,  51,  24, 226,  36, 204, 145]], dtype='uint8'),
##        '殺ピ':np.array([[6, 105, 177,  24, 210, 179, 100,  28]], dtype='uint8'),
##        '狂ピ':np.array([[54,  73, 193,  32,  98, 145,  73, 159]], dtype='uint8'),
        '未ドロップ1':np.array( [[25, 204, 50, 156, 205, 102, 167, 153]], dtype='uint8'),
        '未ドロップ2':np.array( [[152, 102,  51, 158,  77, 102, 230, 153]], dtype='uint8'),
    }


    #魔石を見分けるハッシュ値
    dist_maseki = {
        '剣魔':np.array([[153, 218, 134, 103, 122, 231, 158, 235]], dtype='uint8'),
        '弓魔':np.array([[227, 242, 24, 254, 141, 255, 230, 189]], dtype='uint8'),
        '槍魔':np.array([[ 11,   7, 126, 248, 216, 164, 104,  80]], dtype='uint8'),
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

    #クエストを見分けるハッシュ値
    dist_quest = {
        '冬木':np.array([[ 81,  74,  74, 166, 182, 212, 158, 218]], dtype='uint8'),
        'オルレアン':np.array([[129, 126, 122, 174, 158,  93, 236, 222]], dtype='uint8'),
        'セプテム':np.array([[113,  58, 156, 198, 138, 117, 158, 174]], dtype='uint8'),
        'オケアノス':np.array([[225, 154,  62,  30, 170,  92, 215, 151]], dtype='uint8'),
        'ロンドン':np.array([[241, 158, 110, 170, 126, 124, 191, 186]], dtype='uint8'),
        '北米':np.array([[  1, 174, 250, 222, 137, 174, 214, 141]], dtype='uint8'),
        'キャメロット':np.array([[129, 242, 246,  60, 124, 238, 188, 124]], dtype='uint8'),
        'バビロニア':np.array([[193, 227,  86, 218, 250, 170, 245,  59]], dtype='uint8'),
        '新宿':np.array([[121,  58, 166, 174, 142, 102, 238, 221]], dtype='uint8'),
        'アガルタ':np.array([[145, 206,  78,  58, 170, 243, 114, 235]], dtype='uint8'),
        '下総国':np.array([[113, 122,  86, 102, 170, 154, 170, 115]], dtype='uint8'),
        'セイレム':np.array([[241, 190, 198,  76, 158, 243, 206, 202]], dtype='uint8'),
        'アナスタシア':np.array([[  1, 243, 246, 142,  10, 248, 190, 106]], dtype='uint8'),
        'ゲッテルデメルング':np.array([[ 79, 126,  16, 175, 248,  23, 238, 115]], dtype='uint8'),
        'シン':np.array([[185, 238, 110, 185, 114, 119, 202, 106]], dtype='uint8'),
        'ユガ・クシェートラ':np.array([[  3,  30, 216, 186, 180, 212, 122,  71]], dtype='uint8'),
        'アトランティス':np.array([[ 65,  30,  58, 242, 170, 250,  92, 231]], dtype='uint8'),
        'オリュンポス':np.array([[225, 242,  26,  87,  42, 169, 181, 222]], dtype='uint8'),
    }


    dist_local = {
    }


    def __init__(self, storage=defaultItemStorage):
        self.storage = storage
        self.calc_dist_item()
        self.calc_dist_local()
        self.sozai = {}
        self.sozai_betsumei = {}
        self.read_item()
        self.freequest = {}
        self.read_freequest()
        self.syurenquest = {}
        self.read_syurenquest()

    def read_item(self):
        """
        CSV形式のアイテム変換データを読み込む
        """
        itemfile = Path(__file__).resolve().parent / Path("item.csv")
        with open(itemfile, 'r' , encoding="utf_8") as f:
            try:
                reader = csv.reader(f)
                header = next(reader)  # ヘッダーを読み飛ばしたい時

                for row in reader:
    ##                q = {}
                    for item in row[2:]:
                        if item == "":
                            break
                        self.sozai_betsumei[item] = row[1]
                    self.sozai[row[1]] = row[0]
            except UnicodeDecodeError:
                print("[エラー]item.csv の文字コードがおかしいようです。UTF-8で保存してください。")
                sys.exit()
            except IndexError:
                print("[エラー]item.csv がCSV形式でないようです。")
                sys.exit()

    def normalize_item(self, s):
        for pattern in self.sozai_betsumei.keys():
            if re.match(pattern, s):
                s = re.sub("^" + s + "$", self.sozai_betsumei[pattern], s)
                break
        return s

    def read_freequest(self):
        """
        CSV形式のフリークエストデータを読み込む
        """
        fqfile = Path(__file__).resolve().parent / Path("freequest.csv")

        with open(fqfile, 'r', encoding="utf_8") as f:
            try:
                reader = csv.reader(f)
                header = next(reader)  # ヘッダーを読み飛ばしたい時

                for row in reader:
                    q = {}
                    q["ストーリー"] = row[0]
                    q["特異点"] = row[1]
                    q["場所"] = row[2]
                    d = {}
                    for item in row[4:]:
                        if item == "":
                            break
                        d[self.normalize_item(item)] = []
                    q["ドロップアイテム"] = d
                    self.freequest[row[3]] = q
            except UnicodeDecodeError:
                print("[エラー]freequest.csv の文字コードがおかしいようです。UTF-8で保存してください。")
                sys.exit()
            except IndexError:
                print("[エラー]freequest.csv がCSV形式でないようです。")
                sys.exit()

    def read_syurenquest(self):
        """
        CSV形式の修練クエストデータを読み込む
        """
        syurenfile = Path(__file__).resolve().parent / Path("syurenquest.csv")
        with open(syurenfile, 'r', encoding="utf_8") as f:
            try:
                reader = csv.reader(f)
                header = next(reader)  # ヘッダーを読み飛ばしたい時

                for row in reader:
                    q = {}
                    q["周回数"] = []
                    d = {}
                    for item in row[1:]:
                        if item == "":
                            break
                        d[self.normalize_item(item)] = []
                    q["ドロップアイテム"] = d
                    self.syurenquest[row[0]] = q
            except UnicodeDecodeError:
                print("[エラー]syurenquest.csv の文字コードがおかしいようです。UTF-8で保存してください。")
                sys.exit()
            except IndexError:
                print("[エラー]syurenquest.csv がCSV形式でないようです。")
                sys.exit()

    def calc_dist_local(self):
        """
        既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
        """
        for itemname, img in self.storage.known_item_dict().items():
            self.dist_local[itemname] = self.compute_hash(img)

    def calc_dist_item(self):
        """
        既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
        """
        with open(Item_dist_file, encoding='UTF-8') as f:
            reader = csv.reader(f)
            for row in reader:    
                self.dist_item[row[0]] = np.array([row[1:]], dtype='uint8')
        with open(CE_dist_file, encoding='UTF-8') as f:
            reader = csv.reader(f)
            for row in reader:    
                self.dist_item[row[0]] = np.array([row[2:]], dtype='uint8')


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
        img = img_rgb[int(11/180*height):int(150/180*height),
                        int(23/166*width):int(140/166*width)]
        return DropItems.hasher.compute(img)

class ScreenShot:
    unknown_item_count = 0

    def __init__(self, img_rgb, svm, dropitems, debug=False):
        # TRAINING_IMG_WIDTHは3840x2160の解像度をベースにしている
        TRAINING_IMG_WIDTH = 1514
        threshold = 80
        self.dropitems = dropitems
        self.img_rgb_orig = img_rgb
        self.img_hsv_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.img_gray_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        th, self.img_th_orig = cv2.threshold(self.img_gray_orig,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        self.height, self.width = img_rgb.shape[:2]

        self.error = ""
        self.tokuiten = ""
        try:
            game_screen = self.extract_game_screen(debug)
        except ValueError as e:
            self.error = str(e)
            self.itemlist = []
            self.itemdic = {}
            return

        if debug:
            cv2.imwrite('game_screen.png', game_screen)
            print(self.tokuiten)

        height_g, width_g, _ = game_screen.shape
        if debug:
            print("cutting image size:", end="")
            print(width_g, end="x")
            print(height_g)
        wscale = (1.0 * width_g) / TRAINING_IMG_WIDTH
        resizeScale = 1 / wscale

        if resizeScale > 1:
            matImgResize = 1 / resizeScale
            self.img_rgb = cv2.resize(game_screen, (0,0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_CUBIC)
        else:
            self.img_rgb = cv2.resize(game_screen, (0,0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_AREA)

        if debug:
            cv2.imwrite('game_screen_resize.png', self.img_rgb)

        self.img_gray = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2GRAY)
        self.img_hsv = cv2.cvtColor(self.img_rgb, cv2.COLOR_BGR2HSV)

        item_pts = []
        self.error = ""
        try:
            item_pts = self.img2points()
        except ValueError as e:
            self.error = str(e)

        self.items = []
        template = cv2.imread('syoji_silber.png',0) # Item内で使用
        for i, pt in enumerate(item_pts):
            item_img_rgb = self.img_rgb[pt[1] :  pt[3],  pt[0] :  pt[2]]
            item_img_gray = self.img_gray[pt[1] :  pt[3],  pt[0] :  pt[2]]
            item_img_hsv = self.img_hsv[pt[1] :  pt[3],  pt[0] :  pt[2]]
            if debug:
                cv2.imwrite('item' + str(i) + '.png', item_img_rgb)
            # アイテム枠のヒストグラム調査
            if self.is_empty_box(item_img_hsv) == True: break
            item = Item(item_img_rgb, item_img_gray, svm, dropitems, template, debug)
            if debug == True:
                if item.name.endswith("種火") or item.name.endswith("灯火") or item.name.endswith("大火"):
                    continue
            elif item.name.endswith("火"):
                break
            if item.name == "QP":
                break
            self.items.append(item)
                
        self.itemdic = self.makeitemdict()
        self.itemlist = self.makeitemlist()
        self.deside_freequestname()
        if self.quest_output == "":
            self.deside_syurenquestname()

    def calc_black_whiteArea(self, bw_image):
        image_size = bw_image.size
        whitePixels = cv2.countNonZero(bw_image)
        blackPixels = bw_image.size - whitePixels
     
        whiteAreaRatio = (whitePixels/image_size)*100#[%]
        blackAreaRatio = (blackPixels/image_size)*100#[%]
     
        return whiteAreaRatio

    def is_empty_box(self, img_hsv):
        """
        アイテムボックスにアイテムが無いことを判別する
        """
        lower = np.array([50,20,100]) 
        upper = np.array([200,200,255])

        img_mask = cv2.inRange(img_hsv, lower, upper)
        if self.calc_black_whiteArea(img_mask) > 99:
            return True
        return False
        
    def find_edge(self, img_th, reverse=False):
        """
        直線検出で検出されなかったフチ幅を検出
        """
        edge_width = 8
        ## lx = rx = 0
        height, width = img_th.shape[:2]
        target_color = 255 if reverse else 0
        for i in range(edge_width):
            img_th_x = img_th[:,i:i+1]
            hist = cv2.calcHist([img_th_x],[0],None,[256],[0,256]) #ヒストグラムを計算
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
            if maxLoc[1] == target_color:
                break
        lx = i
        for j in range(edge_width):
            img_th_x = img_th[:,width - j:width - j + 1]
            hist = cv2.calcHist([img_th_x],[0],None,[256],[0,256]) #ヒストグラムを計算
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
            if maxLoc[1] == 0:
                break
        rx = i

        return lx, rx
    def deside_syurenquestname(self):
        itemset = set([i[0] for i in self.itemlist])
        self.quest = "" #クエスト名
        self.place = "" #クエストの場所名
        self.quest_output = "" #周回カウンタに合わせたクエスト名
        for quest in self.dropitems.syurenquest:
##            print(self.dropitems.syurenquest[quest])
            dropset = set([i for i in self.dropitems.syurenquest[quest]["ドロップアイテム"].keys() if not i.endswith("火")])
            if itemset == dropset:
                self.quest_output = quest
                self.droplist = [i for i in self.dropitems.syurenquest[quest]["ドロップアイテム"].keys()]
                break
        
    def deside_freequestname(self):
        """
        クエスト名を決定
        """
        itemset = set([i[0] for i in self.itemlist if not i[0].startswith("泥無しアイテム")])
        self.quest = "" #クエスト名
        self.place = "" #クエストの場所名
        self.quest_output = "" #周回カウンタに合わせたクエスト名
        # reversed するのは 未確認座標X-Cを未確認座標X-Bより先に認識させるため
        for quest in reversed(self.dropitems.freequest):
            if self.dropitems.freequest[quest]["特異点"] == self.tokuiten:
                dropset = set([i for i in self.dropitems.freequest[quest]["ドロップアイテム"].keys() if not i.endswith("火")])
                if itemset == dropset:
                    self.quest = quest
                    self.place = self.dropitems.freequest[quest]["場所"]
                    self.droplist = [i for i in self.dropitems.freequest[quest]["ドロップアイテム"].keys()]
                    break
        if self.place != "":
            quest_list = [quest for quest in self.dropitems.freequest.keys() if self.dropitems.freequest[quest]["特異点"] == self.tokuiten and  self.dropitems.freequest[quest]["場所"] == self.place]
            if self.tokuiten == "北米":
                self.quest_output = self.place + self.quest
            elif len(quest_list) == 1:
                self.quest_output = self.tokuiten + " " + self.place
            else:
                # クエストが0番目のときは場所を出力、それ以外はクエスト名を出力
                if quest_list.index(self.quest) == 0:
                    self.quest_output = self.tokuiten + " " + self.place
                else:
                    self.quest_output = self.tokuiten + " " + self.quest            

    def detect_enemy_tab(self, debug=False):
        """
        「エネミー」タブを探す
        """
        lower = np.array([0,0,0]) 
        upper = np.array([16,16,16]) #ほぼ黒
        img_mask = cv2.inRange(self.img_rgb_orig, lower, upper)
        contours = cv2.findContours(img_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        if debug:
            cv2.imwrite("img_mask.png", img_mask)

        item_pts = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000:
                ret = cv2.boundingRect(cnt)
                pts = [ ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3] ]
                if 4.2 < ret[2]/ret[3] < 4.4:
                    item_pts.append(pts)
        if debug:
            print("エネミータブの位置: ", end="")
            print(item_pts)
        if len(item_pts) == 0:
            raise ValueError("エネミータブ無し")

        return item_pts[0]

    def detect_close_button(self, enemytab_pts, debug=False):
        """
        「閉じる」ボタンを探す
        """
        lower_w = np.array([100,100,100]) 
        upper_w = np.array([255,255,255])
        img_mask_w = cv2.inRange(self.img_rgb_orig, lower_w, upper_w)
        closebutton_pts = []
        contours = cv2.findContours(img_mask_w, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2:
                ret = cv2.boundingRect(cnt)
                pts = [ ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3] ]
                if pts[1] > self.height/2 \
                   and 4.5 < ret[2]/ret[3] < 4.9 and enemytab_pts[0] < pts[2] < enemytab_pts[2] \
                   and enemytab_pts[2] - enemytab_pts[0] > ret[2]:
                    closebutton_pts.append(pts)
        closebutton_pts.sort()
        if debug:
            print("閉じるボタンの位置: ", end="")
            print(closebutton_pts)
        if len(closebutton_pts) == 0:
            raise ValueError("閉じるボタン無し")
        
        if debug:
            cv2.imwrite("img_mask_w.png", img_mask_w)

        return closebutton_pts[0]
    
    def extract_game_screen(self, debug=False):
        """
        1.「エネミー」タブを探す。「エネミー」タブの右端をcut imageの右端とする
        2. 「エネミー」タブの位置情報から「閉じる」ボタンの位置を探す
        3. 「エネミー」タブの右端と「閉じる」ボタンの中心からcut imageの左端を決める
        """
        enemytab_pts = self.detect_enemy_tab(debug)
        closebutton_pts = self.detect_close_button(enemytab_pts, debug)

        right_x = enemytab_pts[2]
        center_x = closebutton_pts[0] + int((closebutton_pts[2] - closebutton_pts[0])/2)
        window_widhth = (right_x - center_x)*2
        left_x = right_x - window_widhth
        upper_y = enemytab_pts[3]
        bottom_y = enemytab_pts[3] + int(1250*(enemytab_pts[3] - enemytab_pts[1])/175)

        if debug:
            print("game_screenの座標: [[", end ="")
            print(left_x, end=", ")
            print(upper_y, end=", ")
            print(right_x, end=", ")
            print(bottom_y, end="")
            print("]]")

        thimg = self.img_th_orig[upper_y:bottom_y,left_x:right_x]
        lx, rx = self.find_edge(thimg, reverse=True)
        left_x = left_x + lx
        right_x = right_x - rx

        game_screen = self.img_rgb_orig[upper_y:bottom_y,left_x:right_x]
        # ここでクエスト名を認識する
        # 左座標
        quest_left = right_x + int((1983-1723)/(1723 - 209)*(right_x -left_x))
        quest_right = right_x + int((3810-1723)/(1723 - 209)*(right_x -left_x))
#        quest_right = right_x + int((3820-1723)/(1723 - 209)*(right_x -left_x))
        quest_top = upper_y - int((631-21)/(1881 - 631)*(bottom_y - upper_y))
#        quest_top = upper_y - int((631-10)/(1881 - 631)*(bottom_y - upper_y))
        quest_bottom = upper_y - int((631-143)/(1881 - 631)*(bottom_y - upper_y))
#        quest_bottom = upper_y - int((631-180)/(1881 - 631)*(bottom_y - upper_y))
        # 有効な座標があるか
        if quest_left > self.width or quest_right > self.width or quest_left < 0 or quest_top < 0:
            return game_screen
##        print(quest_right)
##        print(quest_left)
        if debug:
            print("quest名切り出しの座標: [[", end ="")
            print(quest_left, end=", ")
            print(quest_top, end=", ")
            print(quest_right, end=", ")
            print(quest_bottom, end="")
            print("]]")
        quest = self.img_rgb_orig[quest_top:quest_bottom,quest_left:quest_right]
        lower = np.array([100,100,100]) 
        upper = np.array([255,255,255]) #ほぼ黒
        img_mask = cv2.inRange(quest, lower, upper)

##        cv2.imshow("img", cv2.resize(img_mask, dsize=None, fx=.5, fy=.5))
##        cv2.waitKey(0)
##        cv2.destroyAllWindows()
        hash = self.compute_hash(quest)
        if debug:
            print(hash)
        tokuitens = {}
        for i in self.dropitems.dist_quest.keys():
            d = Item.hasher.compare(hash, self.dropitems.dist_quest[i])
            #同じアイテムでも14離れることあり(IMG_8785)
            if d <= 20:
                tokuitens[i] = d
        tokuitens = sorted(tokuitens.items(), key=lambda x:x[1])

        try:
            tokuiten = next(iter(tokuitens))
        except:
            tokuiten = ""

        if tokuiten != "":
            self.tokuiten = tokuiten[0]
        return game_screen

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

    def generate_item_pts(self, criteria_left, criteria_top, item_width, item_height, margin_width, margin_height):
        """
            ScreenShot#booty_pts() が返すべき座標リストを生成する。
            全戦利品画像が等間隔に並んでいることを仮定している。

            criteria_left ... 左上にある戦利品の left 座標
            criteria_top ... 左上にある戦利品の top 座標
            item_width ... 戦利品画像の width
            item_height ... 戦利品画像の height
            margin_width ... 戦利品画像間の width
            margin_height ... 戦利品画像間の height
        """
        pts = []
        current = (criteria_left, criteria_top, criteria_left + item_width, criteria_top + item_height)
        for j in range(3):
            # top, bottom の y座標を計算
            current_top = criteria_top + (item_height + margin_height) * j
            current_bottom = current_top + item_height
            # x座標を左端に固定
            current = (criteria_left, current_top, criteria_left + item_width, current_bottom)
            for i in range(4):
                # y座標を固定したままx座標をスライドさせていく
                current_left = criteria_left + (item_width + margin_width) * i
                current_right = current_left + item_width
                current = (current_left, current_top, current_right, current_bottom)
                pts.append(current)
        return pts

    def img2points(self):
        """
        戦利品が出現する12(4x3)の座標 [left, top, right, bottom]
        リサイズ後のgamescreenに合うよう設定
        """
        edge = 7
        width = 300
        pts = [[42-edge, 163-edge, 42+width+edge, 163+width+34],[395-edge, 163-edge, 395+width+edge, 163+width+34],
               [747-edge, 163-edge, 747+width+edge, 163+width+34],[1100-edge, 163-edge, 1100+width+edge, 163+width+34],
               [42-edge, 523-edge, 42+width+edge, 523+width+34],[395-edge, 523-edge, 395+width+edge, 523+width+34],
               [747-edge, 523-edge, 747+width+edge, 523+width+34],[1100-edge, 523-edge, 1100+width+edge, 523+width+34],
               [42-edge, 883-edge, 42+width+edge, 883+width+34],[395-edge, 883-edge, 395+width+edge, 883+width+34],
               [747-edge, 883-edge, 747+width+edge, 883+width+34],[1100-edge, 883-edge, 1100+width+edge, 883+width+34],
               ]

        return pts

    def compute_hash(self, img_rgb):
        return Item.hasher.compute(img_rgb)

class Item:
    hasher = cv2.img_hash.PHash_create()
    def __init__(self, img_rgb, img_gray, svm, dropitems, template, debug=False):
        self.img_rgb = img_rgb
        self.img_gray = img_gray
        self.img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.height, self.width = img_rgb.shape[:2]
        self.svm = svm
        self.dropitems = dropitems
        self.template = template
        self.dropnum = self.ocr_digit(debug)
        if debug == True:
            print("ドロップ数: {}".format(self.dropnum))
        self.name = self.classify_item(img_rgb)
        if debug == True:
            if self.name not in DropItems.dist_item.keys() and not self.name.endswith("火"):
                print('"' + self.name + '"', end="")
                self.name = self.classify_item(img_rgb,debug)

    def ocr_digit(self, debug=False):
        """
        戦利品OCR
        「所持」の文字高と数字の文字数の高さの差からフォントサイズを判定
        """
        # 所持の座標を算出
        w, h = self.template.shape[::-1]
        res = cv2.matchTemplate(self.img_gray,self.template,cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where( res >= threshold)
        syoji_pt = []
        for pt in zip(*loc[::-1]):
            syoji_pt = pt
            break
        if len(syoji_pt) == 0:
            return ""
        offset_x = syoji_pt[0] -13
        offset_y = syoji_pt[1] -281

        # 7桁
        if debug: print("7桁読み込み")
        pts7 = [[141, 303, 162, 335],
                [169, 303, 193, 335],
                [189, 303, 212, 335],
                [210, 303, 232, 335],
                [236, 303, 261, 335],
                [258, 303, 280, 335],
                [278, 303, 300, 335]]
        pts = []
        for pt in pts7:
            pt = [pt[0] +offset_x, pt[1] + offset_y, pt[2] + offset_x, pt[3] + offset_y]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        if len(line_lower_white) == 7 and line_lower_white.isdecimal() == True:
            return line_lower_white
        # 6桁
        if debug: print("6桁読み込み")
        pts6 = [[124, 292, 152, 335],
                [151, 292, 182, 335],
                [177, 292, 208, 335],
                [216, 292, 248, 335],
                [244, 292, 272, 335],
                [270, 292, 300, 335]]

        pts = []
        for pt in pts6:
            pt = [pt[0] +offset_x, pt[1] + offset_y, pt[2] + offset_x, pt[3] + offset_y]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        if len(line_lower_white) == 6 and line_lower_white.isdecimal() == True:
            return line_lower_white
        # 5桁
        if debug: print("5桁読み込み")
        pts5 = [[135, 289, 167, 333],
                [165, 289, 200, 333],
                [207, 289, 240, 333],
                [238, 289, 271, 333],
                [269, 289, 300, 333]]
        pts = []
        for pt in pts5:
            pt = [pt[0] +offset_x, pt[1] + offset_y, pt[2] + offset_x, pt[3] + offset_y]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        if len(line_lower_white) == 5 and line_lower_white.isdecimal() == True:
            return line_lower_white
        # 4桁以下
        pts4 = [[149, 285, 186, 333],
                [196, 285, 232, 333],
                [230, 285, 265, 333],
                [263, 285, 300, 333]]
        pts = []
        for pt in pts4:
            pt = [pt[0] +offset_x, pt[1] + offset_y, pt[2] + offset_x, pt[3] + offset_y]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        return(line_lower_white)
            
    def classify_standard_item(self, img, debug=False):
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
            tanebi = next(iter(tanebifiles))
            hash_tanebi_class = self.compute_tanebi_class_hash(img)
            tanebiclassfiles = {}
            for i in self.dropitems.dist_tanebi_class.keys():
                dtc = Item.hasher.compare(hash_tanebi_class, self.dropitems.dist_tanebi_class[i])
                if dtc <= 19: #18離れることがあったので(Screenshot_20200318-140020.png)
                    tanebiclassfiles[i] = dtc
            tanebiclassfiles = sorted(tanebiclassfiles.items(), key=lambda x:x[1])
            if len(tanebiclassfiles) > 0:
                tanebiclass = next(iter(tanebiclassfiles))
                return tanebiclass[0][0] + tanebi[0][1:]
        
        hash_item = self.compute_hash(img) #画像の距離
        if debug == True:
            print(":np.array([" + str(list(hash_item[0])) + "], dtype='uint8'),")
        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in self.dropitems.dist_item.keys():
            d = Item.hasher.compare(hash_item, self.dropitems.dist_item[i])
            if d <= 15:
            # #21 の修正のため15→14に変更して様子見
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

    def make_new_item(self, img):
        """
            未知のアイテムを storage に登録する。
            同時にハッシュ値を計算し dist_local に保存する。

            ただしドロップカウントがない場合は「泥無しアイテム」として管理し
            storage には登録しない。(ハッシュのみ計算し dist_local に保存)

            いずれの場合も、アイテム名を返す。
        """
        if self.dropnum == "":
            ScreenShot.unknown_item_count = ScreenShot.unknown_item_count + 1
            itemname = "泥無しアイテム" + str(ScreenShot.unknown_item_count)
            self.dropitems.dist_local[itemname] = self.compute_hash(img)
            return itemname

        itemname = self.dropitems.storage.create_item(img)
        self.dropitems.dist_local[itemname] = self.compute_hash(img)
        return itemname

    def classify_item(self, img, debug=False):
        """
        アイテム判別器
        """
        item = self.classify_standard_item(img, debug)
        if item == "":
            item = self.classify_local_item(img)
        if item == "":
            item = self.make_new_item(img)
        return self.dropitems.normalize_item(item)

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
        offset_x = 0
        for pt in reversed(pts):
            char = []
            tmpimg = img_gray[pt[1]:pt[3], pt[0] - offset_x:pt[2] - offset_x]
##            cv2.imshow("img", cv2.resize(tmpimg, dsize=None, fx=4., fy=4.))
##            cv2.waitKey(0)
##            cv2.destroyAllWindows()
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
        img = img_rgb[int(11/180*height):int(148/180*height),
                        int(10/166*width):int(156/166*width)]
##        cv2.imshow("img", cv2.resize(img, dsize=None, fx=2., fy=2.))
##        cv2.waitKey(0)
##        cv2.destroyAllWindows()


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
    ## オプションの解析
    parser = argparse.ArgumentParser(description='戦利品画像を読み取る')
    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('file', help='FGOの戦利品スクショ')    # 必須の引数を追加
    parser.add_argument('-d', '--debug', help='デバッグ情報を出力', action='store_true')     
    parser.add_argument('--version', action='version', version=progname + " " + version)

    args = parser.parse_args()    # 引数を解析

    dropitems = DropItems()
    if training.exists() == False:
        print("[エラー]property.xml が存在しません")
        print("python makeprop.py を実行してください")
        sys.exit(1) 
    svm = cv2.ml.SVM_load(str(training))
    file = Path(args.file)
    img_rgb = imread(str(file))
    sc = ScreenShot(img_rgb, svm, dropitems, args.debug)
    if sc.quest_output != "":
        result = "【"+ sc.quest_output + "】"
    else:
        result = ""
    for item in sc.itemlist:
        if not item[0].startswith("未ドロップ"):
            result = result + item[0] + item[1] + '-'
    if len(result) > 0:
        result = result[:-1]
    print(result)
    if  sc.error != "":
        print(sc.error)
