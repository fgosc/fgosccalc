"""
    twitter 関連の共通するルーチンをまとめたモジュール
"""
from pathlib import Path
import re
from io import BytesIO
import logging

import tweepy
import cv2

from . import setting

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
JPEG_QUALITY = 85
ENCODE_PARAM = [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]


def img2media_id(api, img):
    _, encimg = cv2.imencode(".jpg", img, ENCODE_PARAM)
    res = api.media_upload(filename='fgo_screenshot.jpg', file=BytesIO(encimg))
    logger.info('res.media_id: %s', res.media_id)
    return res.media_id

    
def file2media_id(api, file):
    f = Path(file)
    img = cv2.imread(file)
    return img2media_id(api, img)


def set_twitter():
    ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = setting.get_twitter_key()
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)


def do_upload(befores, afters, owneds, func) -> str:
    logger.info('do_upload')
    text = ''
    api = set_twitter()
    media_ids = []
    for before in befores:
        media_ids.append(func(api, before))
    for after in afters:
        media_ids.append(func(api, after))
    if len(befores) == 1:
        logger.info('owneds: %s', owneds)
        if len(owneds) > 0:
            for owned in owneds:
                media_ids.append(func(api, owned))

    logger.info('media_ids: %s', media_ids)
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


def upload_file(args) -> str:
    return do_upload(args.before, args.after,
                     args.owned, file2media_id)


def upload_webfile(befores, afters, owneds) -> str:
    logger.info('check3')
    return do_upload(befores, afters,
                     owneds, img2media_id)
