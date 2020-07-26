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

import img2str

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
CE_dist_file = Path(__file__).resolve().parent / Path("hash_ce.csv")
Item_nickname_file = Path(__file__).resolve().parent / Path("item_nickname.csv")


def make_diff(itemlist1, itemlist2):
    tmplist = []
    for before, after in zip(itemlist1, itemlist2):
            if before[1].isdigit() and after[1].isdigit() and (not before[0].startswith("未ドロップ") and not after[0].startswith("未ドロップ")):
                tmplist.append((after[0], int(after[1])-int(before[1])))
            elif  not after[0].startswith("未ドロップ"):
                tmplist.append((after[0], "NaN"))
               
    result = ""
    sum = 0
    for item in tmplist:
        if str(item[1]).isdigit():
            sum = sum + item[1]
    if sum < 0:
        n = -1
    else:
        n = 1
    newdic = {}
    for item in tmplist:
        if str(item[1]).isdigit():
            newdic[item[0]] = item[1] * n
        else:
            newdic[item[0]] = item[1]            

    return newdic

#恒常アイテム
#ここに記述したものはドロップ数を読み込まない
#順番ルールにも使われる
# 通常 弓→槍の順番だが、種火のみ槍→弓の順番となる
# 同じレアリティの中での順番ルールは不明
std_item = ['実', 'カケラ', '卵', '鏡', '炉心', '神酒', '胆石', '産毛', 'スカラベ',
    'ランプ', '幼角', '根', '逆鱗', '心臓', '爪', '脂', '涙石' ,
    '霊子', '冠', '矢尻', '鈴', 'オーロラ', '指輪', '結氷', '勾玉','貝殻', '勲章',
    '八連', '蛇玉', '羽根', 'ホム', '蹄鉄', '頁', '歯車', 'ランタン', '種', 
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

craft_essence_list = []
with open(CE_dist_file, encoding='UTF-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0].strip() == '':
            continue
        craft_essence_list.append(row[0])

nickname_dic = {}
with open(Item_nickname_file, encoding='UTF-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[0].strip() == '' or row[1].strip() == '':
            continue
        nickname_dic[row[0]] = row[1]


def sorted_dict(d, key):
    keys = sorted(d, key=key)
    nd = {}
    for key in keys:
        nd[key] = d[key]
    return nd


def out_name(d):
    logger.debug('out_name before: %s', d)
    if d[-1] == '_':
        d = d[:-1]
    if d in nickname_dic:
        d = nickname_dic[d]
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
    def __init__(self, item_dict, questname, questdrops):
        """
            item_dict: make_diff() で求めたドロップ差分情報の辞書
            questname: get_questinfo() で求めたフリークエスト名
            questdrops: get_questinfo() で求めたフリークエストのドロップリスト
        """
        self.item_dict = item_dict
        self.questname = questname
        self.questdrops = questdrops
        self.is_freequest = self.questname is not None and len(self.questname) > 0

    def validate_dropitems(self):
        for name in self.item_dict:
            if name not in self.questdrops:
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

        for name, count in self.item_dict.items():
            if name in craft_essence_list:
                craft_essence[out_name(name)] = count
            elif name not in std_item:
                non_standards[out_name(name)] = count
            elif name in skillstone_list:
                gems[name] = count
            elif name in monyupi_list:
                pieces[name] = count
            elif name in tanebi_list:
                raise ValueError('item_dict should not have wisdoms')
            else:
                materials[name] = count

        if self.is_freequest:
            for questdrop in self.questdrops:
                if questdrop in tanebi_list:
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
##            戦利品はすでに順番ルールになっているのでソートしなくてよい
##            sorted_dict(materials, key=lambda s: std_item.index(s)),
##            sorted_dict(gems, key=lambda s: skillstone_list.index(s)),
##            sorted_dict(pieces, key=lambda s: monyupi_list.index(s)),
##            sorted_dict(wisdoms, key=lambda s: tanebi_list.index(s)),
            non_standards,
        )


def get_questinfo(sc1, sc2):
    sc1qname = sc1.quest_output
    sc2qname = sc2.quest_output
    logger.debug('sc1 quest: %s %s', sc1qname, getattr(sc1, 'droplist', None))
    logger.debug('sc2 quest: %s %s', sc2qname, getattr(sc2, 'droplist', None))
    if not sc2qname:
        return '', ''
    if sc1qname and sc1qname != sc2qname:
        return '', ''
    return sc2qname, getattr(sc2, 'droplist', [])


def _print_as_syukai_counter(newdic, dropitems, sc1, sc2):
    """
        旧実装
        FGO 周回カウンタ報告形式で出力する
    """
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
        default='INFO',
        help='loglevel [default: INFO]',
    )
    parser.add_argument(
        '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='output file [default: STDOUT]',
    )
    parser.add_argument(
        '--future',
        action='store_true',
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

    logger.debug('sc1: %s', sc1.itemlist)
    logger.debug('sc2: %s', sc2.itemlist)

    newdic = make_diff(sc1.itemlist, sc2.itemlist)

    if args.future:
        # 新ロジック
        logger.info('use new DropsDiff algorism')
        questname, droplist = get_questinfo(sc1, sc2)

        logger.debug('questname: %s', questname)
        logger.debug('questdrop: %s', droplist)

        obj = DropsDiff(newdic, questname, droplist)
        is_valid = obj.validate_dropitems()
        parsed_obj = obj.parse()
        output = parsed_obj.as_syukai_counter()

        if not is_valid:
            logger.error('スクリーンショットからクエストを特定できません')
            logger.error(output)
            sys.exit(1)
        else:
            args.output.write(output)
    else:
        # 旧ロジック
        _print_as_syukai_counter(newdic, dropitems, sc1, sc2)


if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.loglevel)
    main(args)
