#!/usr/bin/env python3
"""
    fgosccalc CLI フロントエンド
"""

import argparse
import configparser
import logging
import re
import sys
from io import BytesIO
from pathlib import Path

import cv2
import tweepy

import img2str
from lib.setting import setting_file_path
from lib.twitter import create_access_key_secret
from dropitemseditor import (
    DropsDiff,
    get_questinfo,
    make_diff,
    make_owned_diff,
    merge_sc,
    read_owned_ss,
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


def set_twitter():
    last_id = -1
    settingfile = setting_file_path()
    # TODO 以下の config をロードする処理は lib/setting.py に
    # まとめるのが望ましい。将来の課題とする。
    config = configparser.ConfigParser()
    try:
        config.read(settingfile)
        section0 = "search"
        section1 = "auth_info"
        ACCESS_TOKEN = config.get(section1, "ACCESS_TOKEN")
        ACCESS_SECRET = config.get(section1, "ACCESS_SECRET")
        CONSUMER_KEY = config.get(section1, "CONSUMER_KEY")
        CONSUMER_SECRET = config.get(section1, "CONSUMER_SECRET")
        if section0 not in config.sections():
            config.add_section(section0)
        section0cfg = config[section0]

        last_id = section0cfg.get("last_id", last_id)

    except configparser.NoSectionError:
        print("[エラー] setting.iniに不備があります。")
        sys.exit(1)
    if CONSUMER_KEY == "" or CONSUMER_SECRET == "":
        print("[エラー] CONSUMER_KEYとCONSUMER_SECRETを設定してください")
        print("[エラー] 管理者から得られない場合は個別に取得してください")
        sys.exit(1)
    if ACCESS_TOKEN == "" or ACCESS_SECRET == "":
        create_access_key_secret(CONSUMER_KEY, CONSUMER_SECRET)

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)


def file2media_id(api, file):
    quality = 85
    f = Path(file)
    img = cv2.imread(file)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode(".jpg", img, encode_param)
    res = api.media_upload(filename=f.stem + '.jpg', file=BytesIO(encimg))
    return res.media_id


def upload_file(args):
    api = set_twitter()
    media_ids = []

    text = '画像のテスト投稿'
    logger.debug('args.before: %s', args.before)
    logger.debug('args.after: %s', args.after)
    for before in args.before:
        media_ids.append(file2media_id(api, before))
    for after in args.after:
        media_ids.append(file2media_id(api, after))
    if len(args.before) == 1:
        logger.debug('args.owned: %s', args.owned)
        for owned in args.owned:
            media_ids.append(file2media_id(api, owned))

    logger.debug('media_ids: %s', media_ids)
    status_img = api.update_status(status=text, media_ids=media_ids)
    status_text = api.get_status(status_img.id, tweet_mode="extended")
    logger.debug('%s', status_text.full_text)
    pattern = "(?P<url>https://t.co/.+)$"
    m1 = re.search(pattern, status_text.full_text)
    if not m1:
        url = ""
    else:
        url = re.sub(pattern, r"\g<url>", m1.group())
    
    return url


def main(args):
    dropitems = img2str.DropItems()
    svm = cv2.ml.SVM_load(str(img2str.training))
    sc_before = []
    for f in args.before:
        file = Path(f)
        img_rgb = img2str.imread(str(file))
        sc_before.append(img2str.ScreenShot(img_rgb, svm, dropitems))
    sc1 = merge_sc(sc_before)
    sc_after = []
    for f in args.after:
        file = Path(f)
        img_rgb = img2str.imread(str(file))
        sc_after.append(img2str.ScreenShot(img_rgb, svm, dropitems))
    sc2 = merge_sc(sc_after)

    logger.debug('sc_before0: %s', sc_before[0].itemlist)
    if len(sc_before) == 2:
        logger.debug('sc_before1: %s', sc_before[1].itemlist)
    logger.debug('sc1: %s', sc1.itemlist)
    logger.debug('sc_after0: %s', sc_after[0].itemlist)
    if len(sc_after) == 2:
        logger.debug('sc_after1: %s', sc_after[1].itemlist)
    logger.debug('sc2: %s', sc2.itemlist)

    if args.owned:
        code, owned_list = read_owned_ss(args.owned, dropitems, svm)
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
