#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import math
import logging
import sys
import csv

import numpy as np
import cv2
import requests

from storage.filesystem import FileSystemStorage

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
url_quest = "https://api.atlasacademy.io/nice/JP/quest/"

progname = "img2str"
version = "0.2.0"

ID_UNDROPPED = -2
ID_NO_POSESSION = -1
ID_STANDARD_ITEM_MIN = 6501
ID_STANDARD_ITEM_MAX = 6599
ID_GEM_MIN = 6001
ID_GEM_MAX = 6007
ID_MAGIC_GEM_MIN = 6101
ID_MAGIC_GEM_MAX = 6107
ID_SECRET_GEM_MIN = 6201
ID_SECRET_GEM_MAX = 6207
ID_PIECE_MIN = 7001
ID_MONUMENT_MAX = 7107
ID_2ZORO_DICE = 94047708
ID_3ZORO_DICE = 94047709
ID_START = 95000000
ID_EXP_MIN = 9700100
ID_EXP_MAX = 9707500
PRIORITY_REWARD_QP = 9012
ID_NORTH_AMERICA = 93000500
ID_SYURENJYO = 94006800
ID_EVNET = 94000000

# アイテム下部の文字認証用
training = Path(__file__).resolve().parent / Path("property.xml")
item_path = Path(__file__).resolve().parent / Path("item/")
defaultItemStorage = FileSystemStorage(item_path)
drop_file = Path(__file__).resolve().parent / Path("fgoscdata/hash_drop.json")
quest_dir = Path(__file__).resolve().parent / Path("fgoscdata/data/json/")


class DropItems:
    hasher = cv2.img_hash.PHash_create()

    with open(drop_file, encoding='UTF-8') as f:
        drop_item = json.load(f)

    freequest = []
    questfiles = quest_dir.glob('**/*.json')
    for questfile in questfiles:
        try:
            with open(questfile, encoding='UTF-8') as f:
                quest = json.load(f)
                freequest = freequest + quest
        except Exception as e:
            print("{}: ファイルが読み込めません: {}".format(e, questfile))

    # JSONファイルから各辞書を作成
    item_name = {item["id"]: item["name"] for item in drop_item}
    item_shortname = {
                      item["id"]: item["shortname"] for item in drop_item
                      if "shortname" in item.keys()
                      }
    item_type = {
                 item["id"]: item["type"] for item in drop_item
                 if "type" in item.keys()
                }
    item_dropPriority = {
                         item["id"]: item["dropPriority"]
                         for item in drop_item
                        }
    item_background = {
                       item["id"]: item["background"] for item in drop_item
                       if "background" in item.keys()
                      }
    dist_item = {
                 item["id"]: item["phash"] for item in drop_item
                 if "phash" in item.keys()
                }
    dist_secret_gem = {
                       item["id"]: item["phash_class"] for item in drop_item
                       if ID_SECRET_GEM_MIN <= item["id"] <= ID_SECRET_GEM_MAX
                       and "phash_class" in item.keys()
                      }
    dist_magic_gem = {
                      item["id"]: item["phash_class"] for item in drop_item
                      if ID_MAGIC_GEM_MIN <= item["id"] <= ID_MAGIC_GEM_MAX
                      and "phash_class" in item.keys()
                     }
    dist_gem = {
                item["id"]: item["phash_class"] for item in drop_item
                if ID_GEM_MIN <= item["id"] <= ID_GEM_MAX
                and "phash_class" in item.keys()
                }
    exp_list = [
                item["shortname"] for item in drop_item
                if ID_EXP_MIN <= item["id"] < ID_EXP_MAX
               ]

    npz = np.load(Path(__file__).resolve().parent / Path('background.npz'))
    hist_zero = npz["hist_zero"]
    hist_gold = npz["hist_gold"]
    hist_silver = npz["hist_silver"]
    hist_bronze = npz["hist_bronze"]

    dist_local = {
    }

    def __init__(self, storage=defaultItemStorage):
        self.storage = storage
        self.calc_dist_local()

    def calc_dist_local(self):
        """
        既所持のアイテム画像の距離(一次元配列)の辞書を作成して保持
        """
        start_id = ID_START
        for itemname, img in self.storage.known_item_dict().items():
            # id 候補を決める
            for j in range(99999):
                id = j + start_id
                if id in self.item_name.keys():
                    continue
                break

            self.item_name[id] = itemname
            self.item_shortname[id] = itemname
            self.item_dropPriority[id] = 0
            self.item_type[id] = "Item"
            hash = self.compute_hash(img)
            hash_hex = ""
            for h in hash[0]:
                hash_hex = hash_hex + "{:02x}".format(h)
            self.dist_local[id] = hash

    def hex2hash(self, hexstr):
        hashlist = []
        for i in range(8):
            hashlist.append(int('0x' + hexstr[i * 2: i * 2 + 2], 0))
        return np.array([hashlist], dtype='uint8')

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
        img = img_rgb[int(11 / 180 * height):int(148 / 180 * height),
                      int(10 / 166 * width):int(156 / 166 * width)]

        return DropItems.hasher.compute(img)


class ScreenShot:
    unknown_item_id = ID_START

    def __init__(self, img_rgb, svm, dropitems, debug=False):
        # TRAINING_IMG_WIDTHは3840x2160の解像度をベースにしている
        TRAINING_IMG_WIDTH = 1514
        self.dropitems = dropitems
        self.img_rgb_orig = img_rgb
        self.img_hsv_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.img_gray_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        th, self.img_th_orig = cv2.threshold(self.img_gray_orig,
                                             0, 255,
                                             cv2.THRESH_BINARY
                                             + cv2.THRESH_OTSU)
        self.height, self.width = img_rgb.shape[:2]

        self.error = ""
        try:
            game_screen = self.extract_game_screen(debug)
        except ValueError as e:
            self.error = str(e)
            self.itemlist = []
            self.quest_output = ""
            self.quest_list = []
            return

        if debug:
            cv2.imwrite('game_screen.png', game_screen)

        height_g, width_g, _ = game_screen.shape
        logger.debug("cutting image size %s x %s", width_g, height_g)
        wscale = (1.0 * width_g) / TRAINING_IMG_WIDTH
        resizeScale = 1 / wscale

        if resizeScale > 1:
            self.img_rgb = cv2.resize(
                                      game_screen, (0, 0),
                                      fx=resizeScale, fy=resizeScale,
                                      interpolation=cv2.INTER_CUBIC
                                     )
        else:
            self.img_rgb = cv2.resize(
                                      game_screen, (0, 0),
                                      fx=resizeScale, fy=resizeScale,
                                      interpolation=cv2.INTER_AREA
                                     )

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
        syojifile = Path(__file__).resolve().parent / 'syoji_silber.png'
        template = imread(syojifile, 0)  # Item内でも使用
        self.template = template

        ce_zone = True
        for i, pt in enumerate(item_pts):
            tmp_img_gray = self.img_gray[pt[1]: pt[3], pt[0]: pt[2]]
            numbered, offset_x, offset_y = self.calc_offset(tmp_img_gray)
            if numbered:
                ce_zone = False
            through_item = True if (not numbered and not ce_zone) else False

            item_img_rgb = self.img_rgb[
                                        pt[1] + offset_y: pt[3] + offset_y,
                                        pt[0] + offset_x: pt[2] + offset_x
                                       ]
            item_img_gray = self.img_gray[
                                          pt[1] + offset_y: pt[3] + offset_y,
                                          pt[0] + offset_x: pt[2] + offset_x
                                         ]
            item_img_hsv = self.img_hsv[
                                        pt[1] + offset_y: pt[3] + offset_y,
                                        pt[0] + offset_x: pt[2] + offset_x
                                       ]
            if debug:
                cv2.imwrite('item' + str(i) + '.png', item_img_rgb)
            # アイテム枠のヒストグラム調査
            if self.is_empty_box(item_img_gray):
                break
            logger.debug("[Item %d Information]", i)
            item = Item(item_img_rgb, item_img_hsv, item_img_gray, svm,
                        dropitems, through_item, template, debug)
            if ID_STANDARD_ITEM_MIN <= item.id <= ID_STANDARD_ITEM_MAX \
               and numbered is False:
                break
            self.items.append(item)

        self.itemlist = self.makeitemlist()
        self.deside_freequestname()
        self.quest_output = self.make_quest_output(self.quest)
        self.quest_list = self.make_quest_list()

    def calc_offset(self, img_gray):
        # 所持の座標を算出
        w, h = self.template.shape[::-1]
        res = cv2.matchTemplate(img_gray, self.template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)
        syoji_pt = []
        for pt in zip(*loc[::-1]):
            syoji_pt = pt
            break
        if len(syoji_pt) == 0:
            return False, 0, 0
        offset_x = syoji_pt[0] - 13
        offset_y = syoji_pt[1] - 281
        return True, offset_x, offset_y

    @classmethod
    def calc_black_whiteArea(cls, bw_image):
        image_size = bw_image.size
        whitePixels = cv2.countNonZero(bw_image)

        whiteAreaRatio = (whitePixels / image_size) * 100  # [%]

        return whiteAreaRatio

    def is_empty_box(self, img_gray):
        """
        アイテムボックスにアイテムが無いことを判別する
        """
        threshold = 120
        ret, th = cv2.threshold(img_gray, threshold, 255, cv2.THRESH_BINARY)

        if ScreenShot.calc_black_whiteArea(th) > 99:
            return True
        elif ScreenShot.calc_black_whiteArea(th) < 1:
            return True
        return False

    def find_edge(self, img_th, reverse=False):
        """
        直線検出で検出されなかったフチ幅を検出
        """
        edge_width = 3
        height, width = img_th.shape[:2]
        target_color = 255 if reverse else 0
        for i in range(edge_width):
            img_th_x = img_th[:, i:i + 1]
            hist = cv2.calcHist([img_th_x],
                                [0], None, [256], [0, 256])  # ヒストグラムを計算
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
            if maxLoc[1] == target_color:
                break
        lx = i
        for j in range(edge_width):
            img_th_x = img_th[:, width - j:width - j + 1]
            hist = cv2.calcHist([img_th_x],
                                [0], None, [256], [0, 256])  # ヒストグラムを計算
            # 最小値・最大値・最小値の位置・最大値の位置を取得
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
            if maxLoc[1] == 0:
                break
        rx = i

        return lx, rx

    def compare_drop(self, scitem, fqitem):
        """
        フリクエのドロップアイテムと画像のドロップアイテムを比較
        """
        if len(fqitem) > 12:
            fqitem = fqitem[:12]
        if len(scitem) != len(fqitem):
            return False
        for sc, fq in zip(scitem, fqitem):
            if sc["id"] == ID_UNDROPPED:
                if self.dropitems.item_type[fq["id"]] == "Craft Essence":
                    continue
                else:
                    return False
            elif sc["id"] != fq["id"]:
                return False
        return True

    def deside_freequestname(self):
        """
        クエスト名を決定
        """
        itemlist = [
                    {"id": i["id"], "name":i["name"]} for i in self.itemlist
                    if i["id"] != ID_NO_POSESSION
                   ]
        self.quest = ""   # 周回カウンタに合わせたクエスト名
        self.quests = []  # 周回カウンタに合わせたクエスト名(複数対応)
        # reversed するのは 未確認座標X-Cを未確認座標X-Bより先に認識させるため
        for quest in reversed(self.dropitems.freequest):
            droplist = [
                        {"id": i["id"], "name": i["name"]}
                        for i in quest["drop"]
                        if not i["type"] in ["Point", "Exp. UP"]
                        or i["name"] == "QP"
                       ]
            if self.compare_drop(itemlist, droplist):
                self.droplist = [i["name"] for i in quest["drop"]]
                if self.quest == "":
                    self.quest = quest
                self.quests.append(quest)

    def make_quest_list(self, debug=False):
        quest_list = []
        for quest in self.quests:
            quest_list.append(self.make_quest_output(quest))
        return quest_list

    def make_quest_output(self, quest, debug=False):
        output = ""
        if quest != "":
            quest_list = [
                          q["name"] for q in self.dropitems.freequest
                          if q["place"] == quest["place"]
                         ]
            if math.floor(quest["id"] / 100) * 100 == ID_NORTH_AMERICA:
                output = quest["place"] + " " + quest["name"]
            elif math.floor(quest["id"] / 100) * 100 == ID_SYURENJYO:
                output = quest["chapter"] + " " + quest["place"]
            elif math.floor(quest["id"] / 100000) * 100000 == ID_EVNET:
                output = quest["shortname"]
            else:
                # クエストが0番目のときは場所を出力、それ以外はクエスト名を出力
                if quest_list.index(quest["name"]) == 0:
                    output = quest["chapter"] + " " + quest["place"]
                else:
                    output = quest["chapter"] + " " + quest["name"]
        return output

    def detect_enemy_tab(self, debug=False):
        """
        「エネミー」タブを探す
        """
        lower = np.array([0, 0, 0])
        upper = np.array([16, 16, 16])  # ほぼ黒
        img_mask = cv2.inRange(self.img_rgb_orig, lower, upper)
        contours = cv2.findContours(
                                    img_mask,
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE
                                   )[0]

        if debug:
            cv2.imwrite("img_mask.png", img_mask)

        item_pts = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000:
                ret = cv2.boundingRect(cnt)
                pts = [ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3]]
                if 4.2 < ret[2] / ret[3] < 4.4:
                    item_pts.append(pts)
        logger.debug("エネミータブの位置: %s", item_pts)
        if len(item_pts) == 0:
            raise ValueError("エネミータブ無し")

        return item_pts[0]

    def detect_close_button(self, enemytab_pts, debug=False):
        """
        「閉じる」ボタンを探す
        """
        lower_w = np.array([100, 100, 100])
        upper_w = np.array([255, 255, 255])
        img_mask_w = cv2.inRange(self.img_rgb_orig, lower_w, upper_w)
        closebutton_pts = []
        contours = cv2.findContours(
                                    img_mask_w,
                                    cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE
                                   )[0]
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2:
                ret = cv2.boundingRect(cnt)
                pts = [ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3]]
                if pts[1] > self.height / 2 \
                   and 4.5 < ret[2] / ret[3] < 4.9 \
                   and enemytab_pts[0] < pts[2] < enemytab_pts[2] \
                   and enemytab_pts[2] - enemytab_pts[0] > ret[2]:
                    closebutton_pts.append(pts)
        closebutton_pts.sort()
        logger.debug("閉じるボタンの位置: %s", closebutton_pts)
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
        e_pts = self.detect_enemy_tab(debug)
        c_pts = self.detect_close_button(e_pts, debug)

        right_x = e_pts[2]
        center_x = c_pts[0] + int((c_pts[2] - c_pts[0]) / 2)
        window_widhth = (right_x - center_x) * 2
        left_x = right_x - window_widhth
        upper_y = e_pts[3]
        bottom_y = e_pts[3] + int(1250 * (e_pts[3] - e_pts[1]) / 175)

        logger.debug("game_screenの座標: [%d, %d, %d, %d]",
                     left_x, upper_y, right_x, bottom_y)
        if upper_y < 0:
            raise ValueError("上枠トリミングしすぎ")
        if left_x < 0:
            raise ValueError("左枠トリミングしすぎ")

        thimg = self.img_th_orig[upper_y:bottom_y, left_x:right_x]
        lx, rx = self.find_edge(thimg, reverse=True)
        left_x = left_x + lx
        right_x = right_x - rx

        game_screen = self.img_rgb_orig[upper_y:bottom_y, left_x:right_x]
        return game_screen

    def makeitemlist(self):
        """
        """
        itemlist = []
        for item in self.items:
            itemdic = {}
            itemdic["id"] = item.id
            itemdic["name"] = item.name
            itemdic["dropnum"] = item.dropnum
            itemdic["dropPriority"] = item.dropPriority
            itemlist.append(itemdic)
        return itemlist

    def generate_item_pts(self, criteria_left, criteria_top,
                          item_width, item_height,
                          margin_width, margin_height):
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
        current = (
                   criteria_left,
                   criteria_top,
                   criteria_left + item_width,
                   criteria_top + item_height
                  )
        for j in range(3):
            # top, bottom の y座標を計算
            current_top = criteria_top + (item_height + margin_height) * j
            current_bottom = current_top + item_height
            # x座標を左端に固定
            current = (
                       criteria_left,
                       current_top,
                       criteria_left + item_width,
                       current_bottom
                      )
            for i in range(4):
                # y座標を固定したままx座標をスライドさせていく
                current_left = criteria_left + (item_width + margin_width) * i
                current_right = current_left + item_width
                current = (
                           current_left,
                           current_top,
                           current_right,
                           current_bottom
                          )
                pts.append(current)
        return pts

    def img2points(self):
        """
        戦利品が出現する12(4x3)の座標 [left, top, right, bottom]
        リサイズ後のgamescreenに合うよう設定
        """
        edge = 7
        width = 300
        pts = [[42 - edge, 163 - edge, 42 + width + edge, 163 + width + 34],
               [395 - edge, 163 - edge, 395 + width + edge, 163 + width + 34],
               [747 - edge, 163 - edge, 747 + width + edge, 163 + width + 34],
               [1100 - edge,
                163 - edge, 1100 + width + edge, 163 + width + 34],
               [42 - edge, 523 - edge, 42 + width + edge, 523 + width + 34],
               [395 - edge, 523 - edge, 395 + width + edge, 523 + width + 34],
               [747 - edge, 523 - edge, 747 + width + edge, 523 + width + 34],
               [1100 - edge, 523 - edge,
                1100 + width + edge, 523 + width + 34],
               [42 - edge, 883 - edge, 42 + width + edge, 883 + width + 34],
               [395 - edge, 883 - edge, 395 + width + edge, 883 + width + 34],
               [747 - edge, 883 - edge, 747 + width + edge, 883 + width + 34],
               [1100 - edge, 883 - edge,
                1100 + width + edge, 883 + width + 34],
               ]

        return pts


class ScreenShotBefore(ScreenShot):
    '''
    周回後のスクリーンショットを認識してアイテムが「分かってる」状態の
    周回前スクリーンショット
    '''
    def __init__(self, img_rgb, svm, dropitems, itemilst, debug=False):
        # TRAINING_IMG_WIDTHは3840x2160の解像度をベースにしている
        TRAINING_IMG_WIDTH = 1514
        self.dropitems = dropitems
        self.img_rgb_orig = img_rgb
        self.img_hsv_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.img_gray_orig = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        th, self.img_th_orig = cv2.threshold(self.img_gray_orig,
                                             0, 255,
                                             cv2.THRESH_BINARY
                                             + cv2.THRESH_OTSU
                                             )
        self.height, self.width = img_rgb.shape[:2]

        self.error = ""
        try:
            game_screen = self.extract_game_screen(debug)
        except ValueError as e:
            self.error = str(e)
            self.itemlist = []
            self.quest_output = ""
            self.quest_list = []
            return

        if debug:
            cv2.imwrite('game_screen.png', game_screen)

        height_g, width_g, _ = game_screen.shape
        logger.debug("cutting image size %s x %s", width_g, height_g)
        wscale = (1.0 * width_g) / TRAINING_IMG_WIDTH
        resizeScale = 1 / wscale

        if resizeScale > 1:
            self.img_rgb = cv2.resize(
                                      game_screen,
                                      (0, 0),
                                      fx=resizeScale,
                                      fy=resizeScale,
                                      interpolation=cv2.INTER_CUBIC
                                      )
        else:
            self.img_rgb = cv2.resize(
                                      game_screen,
                                      (0, 0),
                                      fx=resizeScale,
                                      fy=resizeScale,
                                      interpolation=cv2.INTER_AREA
                                      )

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
        syojifile = Path(__file__).resolve().parent / 'syoji_silber.png'
        template = imread(syojifile, 0)  # Item内でも使用
        self.template = template

        ce_zone = True
        for i, pt in enumerate(item_pts):
            tmp_img_gray = self.img_gray[pt[1]: pt[3], pt[0]: pt[2]]
            numbered, offset_x, offset_y = self.calc_offset(tmp_img_gray)
            if numbered:
                ce_zone = False
            through_item = True if (not numbered and not ce_zone) else False

            item_img_rgb = self.img_rgb[
                                        pt[1] + offset_y: pt[3] + offset_y,
                                        pt[0] + offset_x: pt[2] + offset_x
                                        ]
            item_img_gray = self.img_gray[
                                          pt[1] + offset_y: pt[3] + offset_y,
                                          pt[0] + offset_x: pt[2] + offset_x
                                          ]
            item_img_hsv = self.img_hsv[
                                        pt[1] + offset_y: pt[3] + offset_y,
                                        pt[0] + offset_x: pt[2] + offset_x
                                        ]
            if debug:
                cv2.imwrite('item' + str(i) + '.png', item_img_rgb)
            # アイテム枠のヒストグラム調査
            if self.is_empty_box(item_img_gray):
                break
            logger.debug("[Item %d Information]", i)
            item = ItemBefore(item_img_rgb, item_img_hsv, item_img_gray, svm,
                              dropitems, through_item,
                              template, itemilst[i], debug)
            if ID_STANDARD_ITEM_MIN <= item.id <= ID_STANDARD_ITEM_MAX \
               and numbered is False:
                break
            self.items.append(item)

        self.itemlist = self.makeitemlist()
        self.deside_freequestname()
        self.quest_output = self.make_quest_output(self.quest)
        self.quest_list = self.make_quest_list()


class Item:
    hasher = cv2.img_hash.PHash_create()

    def __init__(self, img_rgb, img_hsv, img_gray,
                 svm, dropitems, through_item,
                 template, debug=False):
        if self.is_undropped_box(img_hsv):
            self.id = ID_UNDROPPED
            self.name = "未ドロップ"
            self.dropnum = 0
            self.dropPriority = 0
            return
        if through_item:
            self.id = ID_NO_POSESSION
            self.name = "所持数無しアイテム"
            self.dropnum = 0
            self.dropPriority = 0
            return

        self.img_rgb = img_rgb
        self.img_gray = img_gray
        self.img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.height, self.width = img_rgb.shape[:2]
        self.svm = svm
        self.dropitems = dropitems
        self.template = template
        self.dropnum = self.ocr_digit(debug)
        self.background = classify_background(img_rgb, self.dropitems)
        logger.info("background: %s", self.background)
        self.id = self.classify_item(img_rgb, debug)
        self.name = dropitems.item_name[self.id]
        logger.info("アイテム名: %s", self.name)
        logger.info("ドロップ数: %s", self.dropnum)
        self.dropPriority = dropitems.item_dropPriority[self.id]

    def is_undropped_box(self, img_hsv):
        """
        アイテムボックスが「?」すなわち未ドロップであることを判別する
        """
        lower = np.array([0, 0, 50])
        upper = np.array([225, 50, 150])

        img_mask = cv2.inRange(img_hsv, lower, upper)
        if ScreenShot.calc_black_whiteArea(img_mask) > 90:
            return True
        return False

    def ocr_digit(self, debug=False):
        """
        戦利品OCR
        「所持」の文字高と数字の文字数の高さの差からフォントサイズを判定
        """
        # 所持の座標を算出
        w, h = self.template.shape[::-1]
        res = cv2.matchTemplate(
                                self.img_gray,
                                self.template,
                                cv2.TM_CCOEFF_NORMED
                                )
        threshold = 0.7
        loc = np.where(res >= threshold)
        syoji_pt = []
        for pt in zip(*loc[::-1]):
            syoji_pt = pt
            break
        if len(syoji_pt) == 0:
            return ""
        offset_x = syoji_pt[0] - 13
        offset_y = syoji_pt[1] - 281

        # 7桁
        pts7 = [[141, 303, 162, 335],
                [169, 303, 193, 335],
                [189, 303, 212, 335],
                [210, 303, 232, 335],
                [236, 303, 261, 335],
                [258, 303, 280, 335],
                [278, 303, 300, 335]]
        pts = []
        for pt in pts7:
            pt = [
                  pt[0] + offset_x, pt[1] + offset_y,
                  pt[2] + offset_x, pt[3] + offset_y
                  ]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        logger.debug("7桁読み込み %s", line_lower_white)
        if len(line_lower_white) == 7 and line_lower_white.isdecimal():
            return int(line_lower_white)
        # 6桁
        pts6 = [[127, 292, 156, 335],
                [153, 292, 182, 335],
                [181, 292, 210, 335],
                [218, 292, 247, 335],
                [244, 292, 273, 335],
                [271, 292, 300, 335]]

        pts = []
        for pt in pts6:
            pt = [
                  pt[0] + offset_x, pt[1] + offset_y,
                  pt[2] + offset_x, pt[3] + offset_y
                  ]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        logger.debug("6桁読み込み %s", line_lower_white)
        if len(line_lower_white) == 6 and line_lower_white.isdecimal():
            return int(line_lower_white)
        # 5桁
        pts5 = [[135, 289, 167, 333],
                [165, 289, 200, 333],
                [207, 289, 240, 333],
                [238, 289, 271, 333],
                [269, 289, 300, 333]]
        pts = []
        for pt in pts5:
            pt = [
                  pt[0] + offset_x, pt[1] + offset_y,
                  pt[2] + offset_x, pt[3] + offset_y
                  ]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        logger.debug("5桁読み込み %s", line_lower_white)
        if len(line_lower_white) == 5 and line_lower_white.isdecimal():
            return int(line_lower_white)
        # 4桁以下
        pts4 = [[149, 285, 186, 333],
                [196, 285, 232, 333],
                [230, 285, 265, 333],
                [263, 285, 300, 333]]
        pts = []
        for pt in pts4:
            pt = [
                  pt[0] + offset_x, pt[1] + offset_y,
                  pt[2] + offset_x, pt[3] + offset_y
                  ]
            pts.append(pt)
        line_lower_white = self.read_item(self.img_gray, pts)
        if line_lower_white == "":
            return -1
        return(int(line_lower_white))

    def gem_img2id(self, img, gem_dict):
        hash_gem = self.compute_gem_hash(img)
        gems = {}
        for i in gem_dict.keys():
            d2 = Item.hasher.compare(hash_gem, hex2hash(gem_dict[i]))
            if d2 <= 20:
                gems[i] = d2
        gems = sorted(gems.items(), key=lambda x: x[1])
        try:
            gem = next(iter(gems))
            return gem[0]
        except StopIteration:
            return ""

    def zorodice2id(self, img):
        """
        2ゾロダイスと3ゾロダイスを判別する
        """
        threshold = 100
        im_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二値化(閾値100を超えた画素を255にする。)
        _, img_th = cv2.threshold(im_gray, threshold, 255, cv2.THRESH_BINARY)
        if ScreenShot.calc_black_whiteArea(img_th[63:115, 127:187]) > 99:
            return ID_2ZORO_DICE
        return ID_3ZORO_DICE

    def classify_standard_item(self, img, debug=False):
        """
        imgとの距離を比較して近いアイテムを求める
        """
        hash_item = self.dropitems.compute_hash(img)  # 画像の距離
        hash_hex = ""
        for h in hash_item[0]:
            hash_hex = hash_hex + "{:02x}".format(h)
        logger.debug("phash: %s", hash_hex)
        ids = {}
        # 既存のアイテムとの距離を比較
        for i in self.dropitems.dist_item.keys():
            d = Item.hasher.compare(
                                    hash_item,
                                    hex2hash(self.dropitems.dist_item[i])
                                    )
            if i in self.dropitems.item_background.keys():
                item_bg = self.dropitems.item_background[i]
                if d <= 15 and item_bg == self.background:
                    #  #21 の修正のため15→14に変更して様子見
                    #  ポイントと種の距離が8という例有り(IMG_0274)→16に
                    #  バーガーと脂の距離が10という例有り(IMG_2354)→14に
                    ids[i] = d
            else:
                if d <= 15:
                    ids[i] = d

        if len(ids) > 0:
            ids = sorted(
                         sorted(
                                ids.items(),
                                key=lambda x: x[0],
                                reverse=True
                                ),
                         key=lambda x: x[1]
                         )
            logger.debug("Near IDs:  %s", ids)
            id_tupple = next(iter(ids))
            id = id_tupple[0]
            if ID_SECRET_GEM_MIN <= id <= ID_SECRET_GEM_MAX:
                id = self.gem_img2id(img, self.dropitems.dist_secret_gem)
            elif ID_MAGIC_GEM_MIN <= id <= ID_MAGIC_GEM_MAX:
                id = self.gem_img2id(img, self.dropitems.dist_magic_gem)
            elif ID_GEM_MIN <= id <= ID_GEM_MAX:
                id = self.gem_img2id(img, self.dropitems.dist_gem)
            elif ID_2ZORO_DICE <= id <= ID_3ZORO_DICE:
                id = self.zorodice2id(img)

            return id

        return ""

    def classify_local_item(self, img):
        """
        既所持のアイテム画像の距離を計算して保持
        """
        hash_item = self.dropitems.compute_hash(img)  # 画像の距離

        itemfiles = {}
        # 既存のアイテムとの距離を比較
        for i in self.dropitems.dist_local.keys():
            d = Item.hasher.compare(hash_item, self.dropitems.dist_local[i])
            # 同じアイテムでも14離れることあり(IMG_8785)
            if d <= 15:
                itemfiles[i] = d
        if len(itemfiles) > 0:
            itemfiles = sorted(itemfiles.items(), key=lambda x: x[1])
            logger.debug("itemfiles: %s", itemfiles)
            try:
                item = next(iter(itemfiles))
                return item[0]
            except StopIteration:
                return ""
        return ""

    def make_new_item(self, img):
        """
            未知のアイテムを storage に登録する。
            同時にハッシュ値を計算し dist_local に保存する。

            ただしドロップカウントがない場合は「所持数無しアイテム」として管理し
            storage には登録しない。(ハッシュのみ計算し dist_local に保存)

            いずれの場合も、アイテム名を返す。
        """
        ScreenShot.unknown_item_id = ScreenShot.unknown_item_id + 1
        if self.dropnum == "":
            itemname = "所持数無しアイテム"
        else:
            itemname = self.dropitems.storage.create_item(img)
        id = ScreenShot.unknown_item_id
        name = itemname
        shortname = itemname
        hash = self.dropitems.compute_hash(img)
        hash_hex = ""
        for h in hash[0]:
            hash_hex = hash_hex + "{:02x}".format(h)
        self.dropitems.dist_item[id] = hash_hex
        self.dropitems.item_name[id] = name
        self.dropitems.item_shortname[id] = shortname
        self.dropitems.item_dropPriority[id] = 0
        self.dropitems.item_type[id] = "Item"
        return id

    def classify_item(self, img, debug=False):
        """
        アイテム判別器
        """
        id = self.classify_standard_item(img, debug)
        if id != "":
            return id
        id = self.classify_local_item(img)
        if id != "":
            return id
        return self.make_new_item(img)

    def compute_gem_hash(self, img_rgb):
        """
        スキル石クラス判別器
        中央のクラスマークぎりぎりのハッシュを取る
        記述した比率はiPhone6S画像の実測値
        """
        height, width = img_rgb.shape[:2]

        img = img_rgb[
                      int((145 - 16 - 60) / 2 / 145 * height) + 5:
                      int((145 - 16 + 60) / 2 / 145 * height) + 5,
                      int((132 - 52) / 2 / 132 * width):
                      int((132 + 52) / 2 / 132 * width)
                      ]
        #  cv2.imshow("img", cv2.resize(img, dsize=None, fx=4.5, fy=4.5))
        #  cv2.waitKey(0)
        #  cv2.destroyAllWindows()

        return Item.hasher.compute(img)

    def read_item(self, img_gray, pts, upper=False, yellow=False,):
        """
        戦利品の数値をOCRする(エラー訂正有)
        """
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
            # cv2.imshow("img", cv2.resize(tmpimg, dsize=None, fx=4., fy=4.))
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            tmpimg = cv2.resize(tmpimg, (win_size))
            hog = cv2.HOGDescriptor(
                                    win_size,
                                    block_size,
                                    block_stride,
                                    cell_size,
                                    bins
                                    )
            char.append(hog.compute(tmpimg))
            char = np.array(char)
            pred = self.svm.predict(char)
            result = int(pred[1][0][0])
            if int(pred[1][0][0]) == 0:
                break
            lines = lines + chr(result)

        return lines[::-1]


class ItemBefore(Item):
    def __init__(self, img_rgb, img_hsv, img_gray, svm,
                 dropitems, through_item, template, item,
                 debug=False):
        if self.is_undropped_box(img_hsv):
            self.id = ID_UNDROPPED
            self.name = "未ドロップ"
            self.dropnum = 0
            self.dropPriority = 0
            return
        if through_item:
            self.id = ID_NO_POSESSION
            self.name = "所持数無しアイテム"
            self.dropnum = 0
            self.dropPriority = 0
            return

        self.img_rgb = img_rgb
        self.img_gray = img_gray
        self.img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)
        self.height, self.width = img_rgb.shape[:2]
        self.svm = svm
        self.dropitems = dropitems
        self.template = template
        self.dropnum = self.ocr_digit(debug)

        # ここから書き換える
        # 画像と周回前アイテムとの距離が閾値以下ならそのアイテムにする
        hash_item = self.dropitems.compute_hash(self.img_rgb)  # 画像の距離
        hash_id = self.dropitems.dist_item[item["id"]]
        d = ItemBefore.hasher.compare(
                                      hash_item,
                                      hex2hash(hash_id)
                                      )
        if d <= 15:
            self.id = item["id"]
            self.name = item["name"]
            self.dropPriority = item["dropPriority"]
        else:
            self.background = classify_background(img_rgb, self.dropitems)
            logger.info("background: %s", self.background)
            self.id = self.classify_item(img_rgb, debug)
            self.name = dropitems.item_name[self.id]
            logger.info("アイテム名: %s", self.name)
            logger.info("ドロップ数: %s", self.dropnum)
            self.dropPriority = dropitems.item_dropPriority[self.id]


def img_merge(img1, img2, img3):
    img_blue_c1, img_green_c1, img_red_c1 = cv2.split(img1)
    img_blue_c2, img_green_c2, img_red_c2 = cv2.split(img2)
    img_blue_c3, img_green_c3, img_red_c3 = cv2.split(img3)

    img_blue_c = img_blue_c1.ravel()
    img_blue_c = np.append(img_blue_c, img_blue_c2.ravel())
    img_blue_c = np.append(img_blue_c, img_blue_c3.ravel())

    img_green_c = img_green_c1.ravel()
    img_green_c = np.append(img_green_c, img_green_c2.ravel())
    img_green_c = np.append(img_green_c, img_green_c3.ravel())

    img_red_c = img_red_c1.ravel()
    img_red_c = np.append(img_red_c, img_red_c2.ravel())
    img_red_c = np.append(img_red_c, img_red_c3.ravel())

    return cv2.merge((img_blue_c, img_green_c, img_red_c))


def make_img4hist(img):
    height, width = img.shape[:2]
    img1 = img[int(12/314*width):int(20/314*width),
               int(29/314*width):int(283/314*width)]
    img2 = img[int(29/314*width):int(273/314*width),
               int(11/314*width):int(17/314*width)]
    img3 = img[int(29/314*width):int(273/314*width),
               int(297/314*width):int(303/314*width)]
    return img_merge(img1, img2, img3)


def classify_background(img_rgb, dropitems):
    """
    背景判別
    """
    img = make_img4hist(img_rgb)
    target_hist = img_hist(img)
    bg_score = []
    score_z = calc_hist_score(target_hist, dropitems.hist_zero)
    bg_score.append({"background": "zero", "dist": score_z})
    score_g = calc_hist_score(target_hist, dropitems.hist_gold)
    bg_score.append({"background": "gold", "dist": score_g})
    score_s = calc_hist_score(target_hist, dropitems.hist_silver)
    bg_score.append({"background": "silver", "dist": score_s})
    score_b = calc_hist_score(target_hist, dropitems.hist_bronze)
    bg_score.append({"background": "bronze", "dist": score_b})

    bg_score = sorted(bg_score, key=lambda x: x['dist'])
    logger.debug("background dist: %s", bg_score)
    return (bg_score[0]["background"])


def calc_hist_score(hist1, hist2):
    scores = []
    for channel1, channel2 in zip(hist1, hist2):
        score = cv2.compareHist(channel1, channel2, cv2.HISTCMP_BHATTACHARYYA)
        scores.append(score)
    return np.mean(scores)


def img_hist(img):
    hist1 = cv2.calcHist([img], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img], [1], None, [256], [0, 256])
    hist3 = cv2.calcHist([img], [2], None, [256], [0, 256])

    return hist1, hist2, hist3


def hex2hash(hexstr):
    hashlist = []
    for i in range(8):
        hashlist.append(int('0x' + hexstr[i * 2:i * 2 + 2], 0))
    return np.array([hashlist], dtype='uint8')


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


def parse_args():
    # オプションの解析
    parser = argparse.ArgumentParser(description='FGOの戦利品画像を読み取る')
    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('file', help='戦利品スクショ')    # 必須の引数を追加
    parser.add_argument('-d', '--debug', help='デバッグ情報を出力', action='store_true')
    parser.add_argument(
                        '--csv',
                        help='fgoscdata用csv形式で出力',
                        action='store_true'
                        )
    parser.add_argument('-q', '--questid', type=int)
    parser.add_argument(
                        '--loglevel',
                        choices=('warning', 'debug', 'info'),
                        default='warning'
                        )
    parser.add_argument(
                        '--version',
                        action='version',
                        version=progname + " " + version
                        )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.loglevel.upper())
    logger.info('loglevel: %s', args.loglevel)

    if args.questid:
        if not (93000001 < args.questid < 94999999):
            logger.critical('無効な questid です: %d', args.questid)
            exit(1)
        r_get = requests.get(url_quest + str(args.questid) + "/1")
        if r_get.status_code == 404:
            logger.critical('無効な questid です: %d', args.questid)
            exit(1)
        quest = r_get.json()
        logger.debug("quest: %s", quest)

    dropitems = DropItems()
    if training.exists() is False:
        logger.crytical("property.xml が存在しません")
        logger.crytical("python makeprop.py を実行してください")
        exit(1)
    svm = cv2.ml.SVM_load(str(training))
    file = Path(args.file)
    img_rgb = imread(str(file))
    sc = ScreenShot(img_rgb, svm, dropitems, args.debug)
    if len(sc.quest_list) >= 2:
        logger.warning("周回場所の候補が複数あります")
        logger.warning("sc.quest_list: %s", sc.quest_list)
    logger.debug("sc.itemlist: %s", sc.itemlist)
    if args.csv:
        csv_data = [""]
        if len(sc.quest_list) == 1:
            # short name 用に2回加える
            if args.questid:
                csv_data.append(quest["name"])
                csv_data.append(quest["name"])
            else:
                csv_data.append(sc.quest_output)
                csv_data.append(sc.quest_output)
        else:
            csv_data.append("")
            csv_data.append("")
        for item in sc.itemlist:
            try:
                name = dropitems.item_shortname[item["id"]]
                if name.endswith("礼装"):
                    name = item["name"]
            except KeyError:
                name = item["name"]
            csv_data.append(name)
        writer = csv.writer(sys.stdout)
        writer.writerow(csv_data)
    else:
        if args.questid:
            result = "【" + quest["name"] + "】"
        else:
            if len(sc.quest_list) == 1:
                result = "【" + sc.quest_output + "】"
            else:
                result = ""
        for item in sc.itemlist:
            result = result \
                     + item["name"] \
                     + ("_" if item["name"][-1].isdigit() else "") \
                     + str(item["dropnum"]) \
                     + '-'
        if len(result) > 0:
            result = result[:-1]
        print(result)
    if sc.error != "":
        logger.error(sc.error)
