#!/usr/bin/env python3
import urllib.parse
import logging
import configparser
import webbrowser

import tweepy

from lib.setting import setting_file_path, get_twitter_key

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def get_oauth_token(url: str) -> str:
    querys = urllib.parse.urlparse(url).query
    querys_dict = urllib.parse.parse_qs(querys)
    return querys_dict["oauth_token"][0]


def create_access_key_secret(CONSUMER_KEY, CONSUMER_SECRET):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    try:
        redirect_url = auth.get_authorization_url()
        print("次のURLをウェブブラウザで開きます:", redirect_url)
    except tweepy.TweepError:
        logger.critical("リクエストされたトークンの取得に失敗しました。")
        exit(1)

    oauth_token = get_oauth_token(redirect_url)
    print("oauth_token:", oauth_token)
    auth.request_token['oauth_token'] = oauth_token

    # Please confirm at twitter after login.
    webbrowser.open(redirect_url)

    verifier = input("ウェブブラウザに表示されたPINコードを入力してください:")
    auth.request_token['oauth_token_secret'] = verifier

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        logger.critical("リクエストされたトークンの取得に失敗しました。")

    print("access token key:", auth.access_token)
    print("access token secret:", auth.access_token_secret)

    # TODO setting に永続化する処理は setting.py に実装するのがよい。
    # setting.ini に書かれる内容は setting.py が知っているべきなので。
    # これは将来の課題とする。
    config = configparser.ConfigParser()
    section1 = "auth_info"
    config.add_section(section1)
    config.set(section1, "ACCESS_TOKEN", auth.access_token)
    config.set(section1, "ACCESS_SECRET", auth.access_token_secret)
    config.set(section1, "CONSUMER_KEY", CONSUMER_KEY)
    config.set(section1, "CONSUMER_SECRET", CONSUMER_SECRET)

    settingfile = setting_file_path()
    with open(settingfile, "w") as file:
        config.write(file)


if __name__ == '__main__':
    ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = get_twitter_key()
    create_access_key_secret(CONSUMER_KEY, CONSUMER_SECRET)
