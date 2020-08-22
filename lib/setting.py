"""
    setting.ini を管理するモジュール
"""

from pathlib import Path
import configparser
import sys
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def setting_file_path() -> Path:
    return Path(__file__).resolve().parents[1] / 'setting.ini'


def get_setting():
    '''
    setting file から Twitter acess 用のkeyを取得
    '''
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
        logger.critical("setting.iniに不備があります。")
        sys.exit(1)

    return ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET, last_id
##    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
##    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
##    return tweepy.API(auth)

def put_setting(setting):
    config = configparser.ConfigParser()
    section0 = "search"
    section1 = "auth_info"
    config.add_section(section0)
    config.add_section(section1)
    config.set(section1, "ACCESS_TOKEN", str(setting[0]))
    config.set(section1, "ACCESS_SECRET", str(setting[1]))
    config.set(section1, "CONSUMER_KEY", str(setting[2]))
    config.set(section1, "CONSUMER_SECRET", str(setting[3]))    
    config.set(section0, "LAST_ID", str(setting[4]))
    with open("setting.ini", "w") as file:
        config.write(file)

def get_twitter_key():
    ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET = get_setting()[:4]
    if CONSUMER_KEY == "" or CONSUMER_SECRET == "":
        logger.critical("CONSUMER_KEYとCONSUMER_SECRETを設定してください")
        logger.critical("管理者から得られない場合は個別に取得してください")
        sys.exit(1)
    if ACCESS_TOKEN == "" or ACCESS_SECRET == "":
        logger.critical("create_access_key.py を起動して")
        logger.critical("CONSUMER_KEYとCONSUMER_SECRETを設定してください")
        sys.exit(1)
    return ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
