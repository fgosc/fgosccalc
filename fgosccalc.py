#!/usr/bin/env python3
import argparse
import dataclasses
import logging
import sys
import cv2
import numpy as np
from pathlib import Path
from collections import Counter
from typing import List, Dict, Any
import csv
import json

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
drop_file = Path(__file__).resolve().parent / Path("hash_drop.json")

with open(drop_file, encoding='UTF-8') as f:
    drop_item = json.load(f)
item_name = {item["id"]:item["name"] for item in drop_item}
item_shortname = {item["id"]:item["shortname"] for item in drop_item if "shortname" in item.keys()}
item_type = {item["id"]:item["type"] for item in drop_item}
exp_list = [item["shortname"] for item in drop_item if ID_EXP_MIN <= item["id"] < ID_EXP_MAX]

def make_diff(itemlist1, itemlist2):
    tmplist = []
    for before, after in zip(itemlist1, itemlist2):
        diff = after.copy()
        if before["id"] == ID_UNDROPPED or after["id"] == ID_UNDROPPED:
            continue
        elif before["id"] == ID_NO_POSESSION and after["id"] > 0:
            diff["dropnum"] = "NaN"
            tmplist.append(diff)
        elif str(before["dropnum"]).isdigit() and str(after["dropnum"]).isdigit():
            diff["dropnum"] = after["dropnum"] - before["dropnum"]
            tmplist.append(diff)
        else:
            diff["dropnum"] = "NaN"
            tmplist.append(diff)
               
    result = ""
    sum = 0
    for item in tmplist:
        if type(item["dropnum"]) is int:
            sum = sum + item["dropnum"]
    if sum < 0:
        n = -1
    else:
        n = 1
    newlist = []
    for item in tmplist:
        if type(item["dropnum"]) is int:
            item["dropnum"] =  item["dropnum"] *n
        newlist.append(item)            

    return newlist

def out_name(id):
    d = item_name[id]
    logger.debug('out_name before: %s', d)
    if d[-1] == '_':
        d = d[:-1]
    if id in item_shortname.keys():
        d = item_shortname[id]
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
    craft_essence: Dict[str, int]
    materials: Dict[str, int]
    gems: Dict[str, int]
    pieces: Dict[str, int]
    wisdoms: Dict[str, str]
    non_standards: Dict[str, int]

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

            for name, count in cat.items():
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
        def format(item_dict):
            return '-'.join(['{}{}'.format(name, count) for name, count in item_dict.items()])

        def add_line(item_dict, lines):
            line = format(item_dict)
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

    def parse(self):
        """
            素材、スキル石、モニュピ、種火に分解した結果を返す。
        """

        craft_essence = {}
        non_standards = {}
        materials = {}
        gems = {}
        pieces = {}
        wisdoms = {}

        for item in self.item_list:
            if item_type[item["id"]] == "Craft Essence":
                craft_essence[out_name(item["id"])] = item["dropnum"]
            elif ID_STANDARD_ITEM_MIN <= item["id"] <= ID_STANDARD_ITEM_MAX:
                materials[out_name(item["id"])] = item["dropnum"]
            elif ID_GEM_MIN <= item["id"] <= ID_SECRET_GEM_MAX:
                gems[out_name(item["id"])] = item["dropnum"]
            elif ID_PIECE_MIN <= item["id"] <= ID_MONUMENT_MAX:
                pieces[out_name(item["id"])] = item["dropnum"]
            elif ID_EXP_MIN <= item["id"] <= ID_EXP_MAX:
                raise ValueError('item_dict should not have wisdoms')
            else:
                non_standards[out_name(item["id"])] = item["dropnum"]

        if self.is_freequest:
            for questdrop in self.questdrops:
                if questdrop in exp_list:
                    # 種火はスクリーンショットから個数計算できないため常に
                    # NaN (N/A の意味。FGO周回カウンタ互換) を設定する
                    wisdoms[questdrop] = 'NaN'

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
    sc2 = img2str.ScreenShot(img_rgb, svm, dropitems, sc1.tokuiten)

    logger.debug('sc1: %s', sc1.itemlist)
    logger.debug('sc2: %s', sc2.itemlist)

    newdic = make_diff(sc1.itemlist, sc2.itemlist)

    questname, droplist = get_questinfo(sc1, sc2)

    logger.debug('questname: %s', questname)
    logger.debug('questdrop: %s', droplist)

    obj = DropsDiff(newdic, questname, droplist)
    is_valid = obj.validate_dropitems()
    parsed_obj = obj.parse()
    output = parsed_obj.as_syukai_counter()

    if not is_valid:
        logger.info('スクリーンショットからクエストを特定できません')
    args.output.write(output)

if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.loglevel)
    main(args)
