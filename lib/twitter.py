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


def file2media_id(api, file):
    quality = 85
    f = Path(file)
    img = cv2.imread(file)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, encimg = cv2.imencode(".jpg", img, encode_param)
    res = api.media_upload(filename=f.stem + '.jpg', file=BytesIO(encimg))
    return res.media_id


def set_twitter():
    ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = setting.get_twitter_key()
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    return tweepy.API(auth)


def upload_file(args) -> str:
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
        if args.owned:
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
