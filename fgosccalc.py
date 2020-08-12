#!/usr/bin/env python3
import argparse
import dataclasses
import logging
import sys
import cv2
from pathlib import Path
from typing import List, Dict
import copy
import numpy as np

import img2str

ID_GEM_MIN = 6001
ID_SECRET_GEM_MAX = 6207
ID_PIECE_MIN = 7001
ID_MONUMENT_MAX = 7107
ID_EXP_MIN = 9700100
ID_EXP_MAX = 9707500
ID_STANDARD_ITEM_MIN = 6501
ID_STANDARD_ITEM_MAX = 6599
ID_UNDROPPED = -2
ID_NO_POSESSION = -1

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def make_diff(itemlist1, itemlist2, owned=None):
    tmplist = []
    for before, after in zip(itemlist1, itemlist2):
        diff = copy.deepcopy(after)
        diff_b = copy.deepcopy(before)
        if before["id"] == ID_UNDROPPED and after["id"] == ID_UNDROPPED:
            diff["dropnum"] = "NaN"
            tmplist.append(diff)
        elif before["id"] == ID_NO_POSESSION or after["id"] == ID_NO_POSESSION:
            continue
        elif before["id"] == ID_UNDROPPED and after["id"] > 0:
            diff["dropnum"] = "NaN"
            if owned is not None:
                owned_dic = {item["id"]: item["dropnum"] for item in owned}
                if after["id"] in owned_dic.keys():
                    diff["dropnum"] = after["dropnum"] - owned_dic[after["id"]]
            tmplist.append(diff)
        elif before["id"] > 0 and after["id"] == ID_NO_POSESSION:
            # 画像の認識順が周回前後逆の時のエラー対策
            diff_b["dropnum"] = "NaN"
            tmplist.append(before)
        elif str(before["dropnum"]).isdigit() and str(after["dropnum"]).isdigit():
            diff["dropnum"] = after["dropnum"] - before["dropnum"]
            tmplist.append(diff)
        else:
            diff["dropnum"] = "NaN"
            tmplist.append(diff)

##    sum = 0
##    for item in tmplist:
##        if type(item["dropnum"]) is int:
##            sum = sum + item["dropnum"]
##    if sum < 0:
##        n = -1
##    else:
##        n = 1
##    newlist = []
##    for item in tmplist:
##        if type(item["dropnum"]) is int:
##            item["dropnum"] = item["dropnum"] * n
##        newlist.append(item)
##
##    return newlist
    return tmplist


def out_name(id, dropitems):
    d = dropitems.item_name[id]
    logger.debug('out_name before: %s', d)
    if d[-1] == '_':
        d = d[:-1]
    if id in dropitems.item_shortname.keys():
        d = dropitems.item_shortname[id]
    if d[-1].isdigit():
        d = d + '_'
    logger.debug('out_name after: %s', d)
    return d


@dataclasses.dataclass
class ParsedDropsDiff:
    """
        DropsDiff を
         - 礼装 craft_essence
         - 素材 materials
         - スキル石 gems
         - ピースモニュメント pieces
         - 種火 wisdoms
         - 非恒常アイテム non_standards
        に分解したもの。
    """
    questname: str
    craft_essence: List[Dict[str, int]]
    materials: List[Dict[str, int]]
    gems: List[Dict[str, int]]
    pieces: List[Dict[str, int]]
    wisdoms: List[Dict[str, str]]
    non_standards: List[Dict[str, int]]

    def as_json_data(self) -> List[Dict[str, str]]:
        """
            Web 出力に最適化された JSON like なデータを返す。
            つまり辞書のリスト。
            素材のデータのみで、クエスト名は含まない。

            出力例:
            [
                { "id": 1, "material": "爪", "report": 10 },
                { "id": 2, "material": "羽根", "report": 25 },
                { "id": 3, "material": "!弓モニュ", "report": 3 }
            ]
        """
        categories = [
            self.craft_essence,
            self.materials,
            self.gems,
            self.pieces,
            self.wisdoms,
            self.non_standards,
        ]
        data = []
        index = 0
        # 開始時のみ素材名先頭に "!" をつけない
        first_row = True

        for cat in categories:
            # カテゴリごとに改行するため素材名先頭に "!" をつける
            category_head = True

            for item in cat:
                name = item["name"]
                count = item["dropnum"]
                if first_row:
                    item_name = name
                    first_row = False
                    category_head = False
                elif category_head:
                    # Web 上で報告フォーマットを編集するときの改行表現
                    # (FGO 周回カウンタサイト互換)
                    item_name = f'!{name}'
                    category_head = False
                else:
                    item_name = name

                d = {
                    'id': index,
                    'material': item_name,
                    'report': str(count),
                }
                data.append(d)
                index += 1
        return data

    def as_syukai_counter(self):
        """
            周回カウンタ報告形式の文字列を返す
        """
        def format(item_list):
            return '-'.join(['{}{}'.format(item["name"], item["dropnum"]) for item in item_list])

        def add_line(item_list, lines):
            line = format(item_list)
            if line:
                lines.append(line)

        lines = []
        add_line(self.craft_essence, lines)
        add_line(self.materials, lines)
        add_line(self.gems, lines)
        add_line(self.pieces, lines)
        add_line(self.wisdoms, lines)
        add_line(self.non_standards, lines)

        questname = self.questname
        if not questname:
            questname = '(クエスト名)'
        body = '\n'.join(lines)

        return f"""
【{questname}】000周
{body}
#FGO周回カウンタ http://aoshirobo.net/fatego/rc/
""".lstrip()


class DropsDiff:
    def __init__(self, item_list, questname, questdrops):
        """
            item_list: make_diff() で求めたドロップ差分情報の辞書のリスト
            questname: get_questinfo() で求めたフリークエスト名
            questdrops: get_questinfo() で求めたフリークエストのドロップリスト
        """
        self.item_list = item_list
        self.questname = questname
        self.questdrops = questdrops
        self.is_freequest = self.questname is not None and len(self.questname) > 0

    def validate_dropitems(self):
        for item in self.item_list:
            if item["name"] not in self.questdrops:
                return False
        return True

    def parse(self, dropitems):
        """
            素材、スキル石、モニュピ、種火に分解した結果を返す。
        """

        craft_essence = []
        non_standards = []
        materials = []
        gems = []
        pieces = []
        wisdoms = []

        for i, item in enumerate(self.item_list):
            if item["id"] == ID_UNDROPPED:
                print("check")
                if len(self.questdrops) > 0:
                    item_id = [k for k, v in dropitems.item_name.items() if v == self.questdrops[i]][0]
                    if dropitems.item_type[item_id] == "Craft Essence":
                        craft_essence.append({"name": out_name(item_id, dropitems), "dropnum": 0})
            elif dropitems.item_type[item["id"]] == "Craft Essence":
                craft_essence.append({"name": out_name(item["id"], dropitems), "dropnum": item["dropnum"]})
            elif ID_STANDARD_ITEM_MIN <= item["id"] <= ID_STANDARD_ITEM_MAX:
                materials.append({"name": out_name(item["id"], dropitems), "dropnum": item["dropnum"]})
            elif ID_GEM_MIN <= item["id"] <= ID_SECRET_GEM_MAX:
                gems.append({"name": out_name(item["id"], dropitems), "dropnum": item["dropnum"]})
            elif ID_PIECE_MIN <= item["id"] <= ID_MONUMENT_MAX:
                pieces.append({"name": out_name(item["id"], dropitems), "dropnum": item["dropnum"]})
            elif ID_EXP_MIN <= item["id"] <= ID_EXP_MAX:
                raise ValueError('item_dict should not have wisdoms')
            else:
                non_standards.append({"name": out_name(item["id"], dropitems), "dropnum": item["dropnum"]})

        if self.is_freequest:
            for questdrop in self.questdrops:
                if questdrop in dropitems.exp_list:
                    # 種火はスクリーンショットから個数計算できないため常に
                    # NaN (N/A の意味。FGO周回カウンタ互換) を設定する
                    wisdoms.append({"name": questdrop, "dropnum": 'NaN'})

        return ParsedDropsDiff(
            self.questname,
            craft_essence,
            materials,
            gems,
            pieces,
            wisdoms,
            non_standards,
        )


def get_questinfo(sc1, sc2):
    sc1qname = sc1.quest_output
    sc2qname = sc2.quest_output
    logger.debug('sc1 quest: %s %s', sc1qname, getattr(sc1, 'droplist', None))
    logger.debug('sc2 quest: %s %s', sc2qname, getattr(sc2, 'droplist', None))
    if not sc1qname and not sc2qname:
        return '', ''
    if (sc1qname and sc2qname) and sc1qname != sc2qname:
        return '', ''
    if sc2qname:
        return sc2qname, getattr(sc2, 'droplist', [])
    else:
        return sc1qname, getattr(sc1, 'droplist', [])


class OwnedItem(img2str.Item):
    def __init__(self, img_rgb, dropitems, debug=False):

        self.dropitems = dropitems
        self.id = self.classify_standard_item(img_rgb, debug=False)


class OwnedNumber(img2str.Item):
    def __init__(self, img_gray, svm, debug=False):

        pts9 = [[112, 44, 140, 85],
                [140, 44, 168, 85],
                [168, 44, 196, 85],
                [207, 44, 235, 85],
                [235, 44, 263, 85],
                [263, 44, 291, 85],
                [302, 44, 330, 85],
                [330, 44, 358, 85],
                [358, 44, 386, 85]]
        self.svm = svm
        self.num = int(self.read_item(img_gray, pts9))


def calc_pts(img_rgb):
    height, width = img_rgb.shape[:2]
    hsvLower = np.array([50, 0, 0])    # 抽出する色の下限(HSV)
    hsvUpper = np.array([200, 60, 255])    # 抽出する色の上限(HSV)

    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2HSV)  # 画像をHSVに変換
    hsv_mask = cv2.inRange(hsv, hsvLower, hsvUpper)    # HSVからマスクを作成
    contours = cv2.findContours(hsv_mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
    item_pts_l = []
    item_pts_r = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 5000:
            ret = cv2.boundingRect(cnt)
            pts = [ret[0], ret[1], ret[0] + ret[2], ret[1] + ret[3]]
    #        print(ret[2]/ret[3])
            if 4 < ret[2] / ret[3] < 5:
                if ret[0] + ret[2] / 2 < width / 2:
                    item_pts_l.append(pts)
                else:
                    item_pts_r.append(pts)

    item_pts_l.sort(key=lambda x: x[1])
    item_pts_r.sort(key=lambda x: x[1])

    item_pts = []
    for left, right in zip(item_pts_l, item_pts_r):
        item_pts.append(left)
        if right is not None:
            item_pts.append(right)

    return item_pts


def read_owned_ss(owned_files, dropitems, svm):
    TRAINING_IMG_WIDTH = 1152

    ownitems = []
    for file in owned_files:
        img_rgb = img2str.imread(file)

        item_pts = calc_pts(img_rgb)

        width_g = max([pts[2] for pts in item_pts]) - min([pts[0] for pts in item_pts])
        wscale = (1.0 * width_g) / TRAINING_IMG_WIDTH
        resizeScale = 1 / wscale

        if resizeScale > 1:
            game_screen = cv2.resize(img_rgb, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_CUBIC)
        else:
            game_screen = cv2.resize(img_rgb, (0, 0), fx=resizeScale, fy=resizeScale, interpolation=cv2.INTER_AREA)

        item_pts = calc_pts(game_screen)
        offset_x = 506 - item_pts[0][0]
        offset_y = 451 - item_pts[0][1]

        pts = [[294 - offset_x, 369 - offset_y, 481 - offset_x, 572 - offset_y],
               [1004 - offset_x, 369 - offset_y, 1191 - offset_x, 572 - offset_y],
               [294 - offset_x, 599 - offset_y, 481 - offset_x, 802 - offset_y],
               [1004 - offset_x, 599 - offset_y, 1191 - offset_x, 802 - offset_y],
               [294 - offset_x, 829 - offset_y, 481 - offset_x, 1032 - offset_y],
               [1004 - offset_x, 829 - offset_y, 1191 - offset_x, 1032 - offset_y],
               [294 - offset_x, 1059 - offset_y, 481 - offset_x, 1262 - offset_y],
               [1004 - offset_x, 1059 - offset_y, 1191 - offset_x, 1262 - offset_y],
               ]

        item_ids = []
        for pt in pts:
            item = OwnedItem(game_screen[pt[1]: pt[3], pt[0]: pt[2]], dropitems)
            if item.id != "":
                item_ids.append(item.id)
        logger.debug("item_ids: %s", item_ids)

        item_nums = []
        img_gray = cv2.cvtColor(game_screen, cv2.COLOR_BGR2GRAY)
        for pt in item_pts:
            numitem = OwnedNumber(img_gray[pt[1]: pt[3], pt[0]: pt[2]], svm)
            item_nums.append(numitem.num)
        logger.debug("item_num: %s", item_nums)

        for id, num in zip(item_ids, item_nums):
            ownitem = {}
            ownitem["id"] = id
            ownitem["name"] = dropitems.item_name[id]
            ownitem["dropnum"] = num
            ownitems.append(ownitem)
    ownitems = sorted(ownitems, key=lambda x: x['id'])
    code = 0
    prev_id = -1
    output_items = []
    for item in ownitems:
        if item["id"] == prev_id:
            code = -1
            break
        output_items.append(item)
        prev_id = item["id"]
    return code, output_items


def make_owned_diff(itemlist1, itemlist2, owned_list):
    owned_diff = []
    set1 = {item["id"] for item in itemlist1}
    set2 = {item["id"] for item in itemlist2}
    s_diffs = set2 - set1
    for s_diff in s_diffs:
        for owned in owned_list:
            if s_diff == owned["id"]:
                owned_diff.append(owned)
    return owned_diff


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'sc1',
        help='1st screenshot',
    )
    parser.add_argument(
        'sc2',
        help='2nd screenshot',
    )
    parser.add_argument(
        '-o', '--owned',
        nargs='*',
        help='owned item scrennshot',
    )
    parser.add_argument(
        '--loglevel',
        choices=('DEBUG', 'INFO', 'WARNING'),
        default='WARNING',
        help='loglevel [default: WARNING]',
    )
    parser.add_argument(
        '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='output file [default: STDOUT]',
    )
    return parser.parse_args()


def main(args):
    dropitems = img2str.DropItems()
    svm = cv2.ml.SVM_load(str(img2str.training))
    file1 = Path(args.sc1)
    img_rgb = img2str.imread(str(file1))
    sc1 = img2str.ScreenShot(img_rgb, svm, dropitems)

    file2 = Path(args.sc2)
    img_rgb = img2str.imread(str(file2))
    sc2 = img2str.ScreenShot(img_rgb, svm, dropitems)

    if args.owned:
        code, owned_list = read_owned_ss(args.owned, dropitems, svm)
    else:
        code = -1

    logger.debug('sc1: %s', sc1.itemlist)
    logger.debug('sc2: %s', sc2.itemlist)
    if args.owned:
        logger.debug('owned_list: %s', owned_list)

    owned_diff = []
    if code == 0:
        owned_diff = make_owned_diff(sc1.itemlist, sc2.itemlist, owned_list)

    newdic = make_diff(sc1.itemlist, sc2.itemlist, owned=owned_diff)

    questname, droplist = get_questinfo(sc1, sc2)

    logger.debug('questname: %s', questname)
    logger.debug('questdrop: %s', droplist)

    obj = DropsDiff(newdic, questname, droplist)
    is_valid = obj.validate_dropitems()
    parsed_obj = obj.parse(dropitems)
    output = parsed_obj.as_syukai_counter()

    if not is_valid:
        logger.info('スクリーンショットからクエストを特定できません')
    args.output.write(output)


if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.loglevel)
    main(args)
