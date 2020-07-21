#!/usr/bin/env python3
#
# fgosccalcのデータアップデート
#
# FGO game data API https://api.atlasacademy.io/docs を使用
# 新アイテムが実装されたときどれぐらいのスピードで追加されるかは不明です
#
import requests
from pathlib import Path
import codecs
import csv
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

Image_dir = Path(__file__).resolve().parent / Path("data/item/")
Image_dir_ce = Path(__file__).resolve().parent / Path("data/ce/")
CE_blacklist_file = Path(__file__).resolve().parent / Path("ce_bl.txt")
Item_blacklist_file = Path(__file__).resolve().parent / Path("item_bl.txt")
Item_nickname_file = Path(__file__).resolve().parent / Path("std_item_nickname.csv")
Misc_dir = Path(__file__).resolve().parent / Path("data/misc/")
CE_output_file = Path(__file__).resolve().parent / Path("hash_ce.csv")

Item_output_file = Path(__file__).resolve().parent / Path("hash_item.csv")
if not Image_dir.is_dir():
    Image_dir.mkdir()
if not Image_dir_ce.is_dir():
    Image_dir_ce.mkdir()
if not Misc_dir .is_dir():
    Misc_dir .mkdir()

url_ce = "https://api.atlasacademy.io/export/JP/nice_equip.json"
url_item = "https://api.atlasacademy.io/export/JP/nice_item.json"

bg_files = {"zero":"listframes0_bg.png",
           "bronze":"listframes1_bg.png",
           "silver":"listframes2_bg.png",
           "gold":"listframes3_bg.png",
           "questClearQPReward":"listframes4_bg.png"
           }

bg_rarity = {3:"silver",
             4:"gold",
             5:"gold"}

bg_url = "https://raw.githubusercontent.com/atlasacademy/aa-db/master/build/assets/list/"
star_url = "https://raw.githubusercontent.com/atlasacademy/aa-db/master/build/assets/"
bg_image = {}
for bg in bg_files.keys():
    filename = Misc_dir / bg_files[bg]
    if filename.is_file() == False:
        url_download = bg_url + bg_files[bg]
        response = requests.get(url_download)
        with open(filename, 'wb') as saveFile:
            saveFile.write(response.content)
    tmpimg = cv2.imread(str(filename))
    h, w = tmpimg.shape[:2]
    bg_image[bg] = tmpimg[5:h-5,5:w-5]

hasher = cv2.img_hash.PHash_create()

servant_class = {'saber':'剣',
                 'lancer':'槍',
                 'archer':'弓',
                 'rider':'騎',
                 'caster':'術',
                 'assassin':'殺',
                 'berserker':'狂',
                 'ruler':'裁',
                 'avenger':'讐',
                 'alterEgo':'分',
                 'moonCancer':'月',
                 'foreigner':'降'}


class CvOverlayImage(object):
    """
    [summary]
      OpenCV形式の画像に指定画像を重ねる
    
    https://qiita.com/Kazuhito/items/ff4d24cd012e40653d0c
    """

    def __init__(self):
        pass

    @classmethod
    def overlay(
            cls,
            cv_background_image,
            cv_overlay_image,
            point,
    ):
        """
        [summary]
          OpenCV形式の画像に指定画像を重ねる
        Parameters
        ----------
        cv_background_image : [OpenCV Image]
        cv_overlay_image : [OpenCV Image]
        point : [(x, y)]
        Returns : [OpenCV Image]
        """
        overlay_height, overlay_width = cv_overlay_image.shape[:2]

        # OpenCV形式の画像をPIL形式に変換(α値含む)
        # 背景画像
        cv_rgb_bg_image = cv2.cvtColor(cv_background_image, cv2.COLOR_BGR2RGB)
        pil_rgb_bg_image = Image.fromarray(cv_rgb_bg_image)
        pil_rgba_bg_image = pil_rgb_bg_image.convert('RGBA')
        # オーバーレイ画像
        cv_rgb_ol_image = cv2.cvtColor(cv_overlay_image, cv2.COLOR_BGRA2RGBA)
        pil_rgb_ol_image = Image.fromarray(cv_rgb_ol_image)
        pil_rgba_ol_image = pil_rgb_ol_image.convert('RGBA')

        # composite()は同サイズ画像同士が必須のため、合成用画像を用意
        pil_rgba_bg_temp = Image.new('RGBA', pil_rgba_bg_image.size,
                                     (255, 255, 255, 0))
        # 座標を指定し重ね合わせる
        pil_rgba_bg_temp.paste(pil_rgba_ol_image, point, pil_rgba_ol_image)
        result_image = \
            Image.alpha_composite(pil_rgba_bg_image, pil_rgba_bg_temp)

        # OpenCV形式画像へ変換
        cv_bgr_result_image = cv2.cvtColor(
            np.asarray(result_image), cv2.COLOR_RGBA2BGRA)

        return cv_bgr_result_image
    
def compute_hash_inner(img_rgb):
    img = img_rgb[34:104,:]    

    return hasher.compute(img)

def compute_hash(img_rgb):
    """
    判別器
    この判別器は下部のドロップ数を除いた部分を比較するもの
    記述した比率はiPpd2018画像の実測値
    """
    height, width = img_rgb.shape[:2]
    img = img_rgb[int(11/180*height):int(148/180*height),
                    int(10/166*width):int(156/166*width)]

##    cv2.imshow("img", cv2.resize(img_rgb, dsize=None, fx=2., fy=2.))
##    cv2.waitKey(0)
##    cv2.destroyAllWindows()
    return hasher.compute(img)

def compute_hash_ce(img_rgb):
    """
    判別器
    この判別器は下部のドロップ数を除いた部分を比較するもの
    記述した比率はiPpd2018画像の実測値
    """
    height, width = img_rgb.shape[:2]
    img = img_rgb[5:115,3:119]

##    cv2.imshow("img", cv2.resize(img, dsize=None, fx=2., fy=2.))
##    cv2.waitKey(0)
##    cv2.destroyAllWindows()
    return hasher.compute(img)

def search_item_file(url, savedir):
    """
    url に該当するファイルを返す
    すでに存在したらダウンロードせずそれを使う
    """
    url_download = url
    tmp = url_download.split('/')
    savefilename = tmp[-1]
    Image_file = savedir / Path(savefilename)
    if savedir.is_dir() == False:
        savedir.mkdir()
    if Image_file.is_file() == False:
        response = requests.get(url_download)
        with open(Image_file, 'wb') as saveFile:
            saveFile.write(response.content)
    return Image_file

def overray_item(name, background, foreground):
    """
    枠画像とアイテム画像を合成する
    """
    bg_height, bg_width = background.shape[:2]
    if name.endswith("魔石"):
        foreground = foreground[:,:100-16]
    fg_height, fg_width = foreground.shape[:2]
    if name in ["セイバーピース","セイバーモニュメント"]:
        point = (int((bg_width-fg_width)/2)-3, 131-fg_height)
    elif name in ["アーチャーピース","アーチャーモニュメント"]:
        point = (int((bg_width-fg_width)/2)-8, 131-fg_height)
    elif name in ["ランサーピース","ランサーモニュメント"]:
        point = (int((bg_width-fg_width)/2), 131-fg_height)
    elif name in ["ライダーピース","ライダーモニュメント"]:
        point = (int((bg_width-fg_width)/2)+7, 131-fg_height)
    elif name in ["キャスターピース","キャスターモニュメント"]:
        point = (int((bg_width-fg_width)/2)-1, 131-fg_height)
    elif name in ["アサシンピース","アサシンモニュメント"]:
        point = (int((bg_width-fg_width)/2)+6, 131-fg_height)
    elif name in ["バーサーカーピース","バーサーカーモニュメント"]:
        point = (int((bg_width-fg_width)/2)-3, 131-fg_height)
    else:
        point = (int((bg_width-fg_width)/2), int((bg_height-14-fg_height)/2))
    # 合成
    image = CvOverlayImage.overlay(background,
                                   foreground,
                                   point)
    return image

def overray_ce(background, foreground):
    bg_height, bg_width = background.shape[:2]
    fg_height, fg_width = foreground.shape[:2]

    point = (bg_width-fg_width-5, bg_height-fg_height-5)
    # 合成
    image = CvOverlayImage.overlay(background,
                                   foreground,
                                   point)
    # 縮小 128→124
    wscale = (1.0 * 128) / 124
    resizeScale = 1 / wscale

    image = cv2.resize(image, (0,0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_AREA)

    return image

def name2nickname(name, item_nickname):
    #名前変換
    for i in item_nickname:
        if i["name"] == name:
            if i["nickname"] != "":
                name = i["nickname"]
                break
    return name

def make_item_data():
    """
    アイテムデータを作成
    """
    item_output =[]
    r_get = requests.get(url_item)

    item_list = r_get.json()
    with open(Item_blacklist_file, encoding='UTF-8') as f:
        bl_item = [s.strip() for s in f.readlines()]

    with open(Item_nickname_file, encoding='UTF-8') as f:
        reader = csv.DictReader(f)
        item_nickname = [row for row in reader]

    for item in tqdm(item_list):

        name = item["name"]
        if item["type"] not in ["qp", "questRewardQp", "skillLvUp", "tdLvUp", "eventItem", "dice"]:
            continue
        # 除外アイテムは読み込まない
        if name in bl_item:
            continue
        Image_file = search_item_file(item["icon"], Image_dir /str(item["background"]))
        fg_image = cv2.imread(str(Image_file), cv2.IMREAD_UNCHANGED)
        image = overray_item(name, bg_image[item['background']], fg_image)
        hash = compute_hash(image)
        out = ""
        for h in hash[0]:
            out = out + "{:02x}".format(h)
        tmp = [name2nickname(name, item_nickname)] + [out]
        item_output.append(tmp)

    header = ["name", "phash"]
    with open(Item_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(item_output)

def make_star_data():
    for i in range(3):
        filename = Misc_dir / ("star"  + str(i + 3) + ".png")
        if filename.is_file() == False:
            url_download = star_url + filename.name
            response = requests.get(url_download)
            with open(filename, 'wb') as savefile:
                savefile.write(response.content)    

def make_ce_data():
    make_star_data()
    ce_output =[]

    r_get = requests.get(url_ce)

    ce_list = r_get.json()
    with open(CE_blacklist_file, encoding='UTF-8') as f:
        bl_ces = [s.strip() for s in f.readlines()]
    for ce in tqdm(ce_list):
        if ce["rarity"] <= 2:
            continue
        name = ce["name"]
        if ce["atkMax"]-ce["atkBase"]+ce["hpMax"]-ce["hpBase"]==0 \
           and not ce["name"].startswith("概念礼装EXPカード："):
            continue
        # 除外礼装は読み込まない
        if name in bl_ces:
            continue
        mylist = list(ce['extraAssets']['faces']['equip'].values())
        Image_file =  search_item_file(mylist[0], Image_dir_ce /str(ce["rarity"]))
        ce_image = cv2.imread(str(Image_file))
        # IMREAD_UNCHANGEDを指定しα込みで読み込む
        star_image = cv2.imread(str(Misc_dir / ("star" + str(ce["rarity"]) + ".png")), cv2.IMREAD_UNCHANGED)
        image = overray_ce(ce_image, star_image)
        hash = compute_hash_ce(image)
        out = ""
        for h in hash[0]:
            out = out + "{:02x}".format(h)
        tmp = [name] + [ce['rarity']] + [out]
        ce_output.append(tmp)            

    header = ["name", "rarity", "phash"]
    with open(CE_output_file, 'w', encoding="UTF-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(ce_output)


if __name__ == '__main__':
    make_ce_data()
    make_item_data()
