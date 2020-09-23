#!/usr/bin/env python3
"""
    fgosccalc CLI フロントエンド
"""

import argparse
import logging
import re
import sys
from io import BytesIO
from pathlib import Path

import cv2

import img2str
##from lib.setting import setting_file_path
##from lib.twitter import create_access_key_secret
from lib.twitter import upload_file
from dropitemseditor import (
    DropsDiff,
    get_questinfo,
    make_diff,
    make_owned_diff,
    merge_sc,
    read_owned_ss,
    detect_missing_item
)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b', '--before',
        nargs='+',
        required=True,
        help='1st screenshot(s)',
    )
    parser.add_argument(
        '-a', '--after',
        nargs='+',
        required=True,
        help='2nd screenshot(s)',
    )
    parser.add_argument(
        '-o', '--owned',
        nargs='+',
        help='owned item scrennshot(s)',
    )
    parser.add_argument(
        '-u', '--upload',
        action='store_true',
        help='upload images on twiter',
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
    # 素材が埋まっている可能性が高い周回後スクショから認識する
    sc_after = []
    for f in args.after:
        file = Path(f)
        img_rgb = img2str.imread(str(file))
        sc_after.append(img2str.ScreenShot(img_rgb, svm, dropitems))
    sc2 = merge_sc(sc_after)
    logger.debug('sc_after0: %s', sc_after[0].itemlist)
    if len(sc_after) == 2:
        logger.debug('sc_after1: %s', sc_after[1].itemlist)
    logger.debug('sc2: %s', sc2.itemlist)

    sc_before = []
    for i, f in enumerate(args.before):
        file = Path(f)
        img_rgb = img2str.imread(str(file))
        sc_before.append(img2str.ScreenShotBefore(img_rgb, svm, dropitems, sc_after[i].itemlist))
    sc1 = merge_sc(sc_before)

    logger.debug('sc_before0: %s', sc_before[0].itemlist)
    if len(sc_before) == 2:
        logger.debug('sc_before1: %s', sc_before[1].itemlist)
    logger.debug('sc1: %s', sc1.itemlist)

    # 足りないアイテムを求める
    miss_items = detect_missing_item(sc2, sc1)
 
    if args.owned:
        code, owned_list = read_owned_ss(args.owned, dropitems, svm, miss_items)
    else:
        code = -1

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
    url = ""
    if args.upload:
        url = upload_file(args)
    output = parsed_obj.as_syukai_counter(url)

    if not is_valid:
        logger.info('スクリーンショットからクエストを特定できません')
    args.output.write(output)


if __name__ == '__main__':
    args = parse_args()
    logger.setLevel(args.loglevel)
    if len(args.before) != len(args.after):
        logger.critical('前後でスクショ数が合いません')
        exit(1)
    elif len(args.before) > 2:
        logger.critical('3ペア以上のスクショ比較には対応していません')
        exit(1)
    main(args)
