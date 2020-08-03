#!/usr/bin/env python3
import tweepy
import img2str
import cv2
import re
import requests
import argparse
import numpy as np
import sys
import os
import csv
import unicodedata
import configparser
import urllib
import webbrowser
from pathlib import Path
import json

progname = "FGOツイートスクショチェック"
version = "0.1.0"

MAXSERCH = 100 # --auto オプションで1度の検索で取得するツイート
MAX_LOOP = 5 # --auto オプションでMAXSERCH 件取得を何回行うか

drop_file = Path(__file__).resolve().parent / Path("hash_drop.json")

with open(drop_file, encoding='UTF-8') as f:
    drop_item = json.load(f)

item_name = {item["id"]:item["name"] for item in drop_item}
item_shortname = {item["id"]:item["shortname"] for item in drop_item if "shortname" in item.keys()}
alias2id = {}
for item in drop_item:
    alias2id[item["name"]] = item["id"]
    if "shortname"in item.keys():
        alias2id[item["shortname"]] = item["id"]
    if "alias"in item.keys():
        for a in item["alias"]:
            alias2id[a] = item["id"]

def make_itemdic(s):
    """
    入力テキストからドロップアイテムとその数を抽出
    辞書に保存
    """
    # 辞書にいれる
    items = {}
    s = unicodedata.normalize("NFKC", s)
    s = s.replace(",", "") #4桁の場合 "," をいれる人がいるので
    # 1行1アイテムに分割
    # chr(8211) : enダッシュ
    # chr(8711) : Minus Sign
##        splitpattern = "(-|" + chr(8711) + "|" +chr(8722) + "|\n)"
    splitpattern = "[-\n"+ chr(8711) +chr(8722) +"]"
    itemlist = re.split(splitpattern, s)

    #アイテムがでてくるまで行を飛ばす
    error_flag = False
    for item in itemlist:
##        # なぜかドロップ率をいれてくる人がいるので、カッコを除く
##            item =re.sub("\([^\(\)]*\)$", "", item.strip()).strip()

        if len(item) == 0: #空行は無視
            continue
        if item.endswith("NaN"):
            items[item.replace("NaN", "")] = "NaN"
            continue
        if item.endswith("?"):
            items[item.replace("?", "")] = "?"
            continue

        # ボーナスを表記してくるのをコメント扱いにする「糸+2」など
        if re.search("\+\d$", item):
            continue

        pattern = "(?P<name>^.*\D)(?P<num>\d+$)"
        m = re.search(pattern, item)
        if not m: #パターンに一致しない場合コメント扱いにする
            continue
##        tmpitem = normalize_item(re.sub(pattern, r"\g<name>", item).strip())
        tmpitem = (re.sub(pattern, r"\g<name>", item).strip())
        if " " in tmpitem:
            continue
        else:
            if tmpitem in alias2id.keys():
                tmpitem = item_shortname[alias2id[tmpitem]]
            num = int(re.sub(pattern, r"\g<num>", item))
            items[tmpitem] = num

    return items
    
def make_data4tweet(report):
    ##複数報告検知
    place_pattern = "【(?P<place>[\s\S]+?)】"
    if len(re.findall(place_pattern, report)) > 1:
        return {}

    pattern = "【(?P<place>[\s\S]+)】(?P<num>[\s\S]+?)周(?P<num_after>.*?)\n(?P<items>[\s\S]+?)#FGO周回カウンタ"
    if len(re.findall(pattern, report)) < 1:
        return {}
    
    m = re.search(pattern, report)
   
    #アイテム記述部分
    items = re.sub(pattern, r"\g<items>", m.group())
    return (make_itemdic(items))

def calc_iamge_diff(status, savelocal=False, debug=False):
    if not hasattr(status, 'extended_entities'):    
        return {}, {}

    error_dic = {}
    if 'media' in status.extended_entities:
        # 重い処理なのでこのプログラム場合はエラー判定後に実行
        dropitems = img2str.DropItems()        
        svm = cv2.ml.SVM_load(str(img2str.training))

        itemlists = []
        for i, media in enumerate(status.extended_entities['media']):
            response = requests.get(media['media_url'] + ':orig')
            if response.status_code != requests.codes.ok:
                url = media['media_url'].replace(".jpg", "") + "?format=jpg&name=4096x4096"
                response = requests.get(url)
                if response.status_code != requests.codes.ok:
                    error_dic["image" + str(i+1)] = response.status_code
                    break
                    response.raise_for_status()
            tmp = response.content
            img_buf = np.frombuffer(tmp, dtype='uint8')
            image = cv2.imdecode(img_buf, 1)
            sc = img2str.ScreenShot(image, svm, dropitems, debug)
            if savelocal:
                Image_dir = Path(__file__).resolve().parent / Path("image/")
                Image_file = Image_dir / Path(status.id_str + "_" + str(i) + ".jpg")
                if not Image_dir.is_dir():
                    Image_dir.mkdir()
                cv2.imwrite(str(Image_file), image)
            if sc.error != "":
                error_dic["image" + str(i+1)] = sc.error
            itemlists.append(sc.itemlist)
            if debug:
                print("画像" + str(i + 1), end=",")
                for j in sc.itemlist:
                    print (j["name"], end=",")
                print()
                print("画像" + str(i + 1), end=",")
                for j in sc.itemlist:
                    print (j["name"], end=",")
                    print (j["dropnum"], end=",")
                print()
        ## 通常素材が埋まって無い報告は無いと推測してそういう報告は無効と判断
            new_itemlists = []                    
            for itemlist in itemlists:
                for item in itemlist:
                    if item["id"] in dropitems.dist_item.keys():
                        new_itemlists.append(itemlist)
                        break

    item_dic = {}
    if debug:
        print(new_itemlists)
    #戦利品スクショでないものはスキップして new_listを作成
    if len(new_itemlists) == 4:
        for before1, after1, before2, after2 \
            in zip(new_itemlists[0], new_itemlists[1],
                   new_itemlists[2], new_itemlists[3]):
            if str(before1["dropnum"]).isdigit() and str(after1["dropnum"]).isdigit() \
               and str(before2["dropnum"]).isdigit() and str(after2["dropnum"]).isdigit() \
               and not before1["id"] < 0 and not after1["id"] < 0 \
                    and not before2["id"] < 0 and not after2["id"] < 0:
                item_dic[item_shortname[after1["id"]]] = after1["dopnum"]-before1["dopnum"] + after2["dopnum"]-before2["dopnum"]      
    elif len(new_itemlists) >= 2:
        for before, after in zip(new_itemlists[0], new_itemlists[1]):
            if str(before["dropnum"]).isdigit() and str(after["dropnum"]).isdigit() \
               and not before["id"] < 0 and not after["id"] < 0:
                if after["id"] in item_shortname.keys():
                    name = item_shortname[after["id"]]
                else:
                    name = item_name[after["id"]]
                item_dic[name] = int(after["dropnum"])-int(before["dropnum"])

    # 報告前と報告後の後の画像順が逆の場合の対策
    sum = 0
    for n in item_dic.values():
        sum = sum + n
    if sum < 0:
        for item in item_dic:
            item_dic[item] = item_dic[item] * -1
                   
    return item_dic, error_dic

def dic2str(item_dic):
    """
    アイテム辞書形式を周回カウンタ文法に変換
    """
    result = ""
    for item in item_dic.keys():
        result = result + item + str(item_dic[item]) + '-'
    if len(result) > 0:
        result = result[:-1]
    return result

def calc_diff(report_dic, image_dic, inverse=False):
    result_dic = {}
    for item in report_dic.keys():
        if item in image_dic.keys():
            if str(report_dic[item]).isdigit():
                if inverse == False:
                    result_dic[item] = report_dic[item] - image_dic[item]
                else:
                    result_dic[item] = report_dic[item] + image_dic[item]                    
    return result_dic

def get_oauth_token(url:str)->str:
    querys = urllib.parse.urlparse(url).query
    querys_dict = urllib.parse.parse_qs(querys)
    return querys_dict["oauth_token"][0]

def create_access_key_secret(CONSUMER_KEY, CONSUMER_SECRET):
#if __name__ == '__main__':

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

    try:
        redirect_url = auth.get_authorization_url()
        print ("次のURLをウェブブラウザで開きます:",redirect_url)
    except tweepy.TweepError:
        print( "[エラー] リクエストされたトークンの取得に失敗しました。")
        sys.exit(1)


    oauth_token = get_oauth_token(redirect_url)
    print("oauth_token:", oauth_token)
    auth.request_token['oauth_token'] = oauth_token

    # Please confirm at twitter after login.
    webbrowser.open(redirect_url)

#    verifier = input("You can check Verifier on url parameter. Please input Verifier:")
    verifier = input("ウェブブラウザに表示されたPINコードを入力してください:")
    auth.request_token['oauth_token_secret'] = verifier

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('[エラー] アクセストークンの取得に失敗しました。')

    print("access token key:",auth.access_token)
    print("access token secret:",auth.access_token_secret)

    config = configparser.ConfigParser()
    section1 = "auth_info"
    config.add_section(section1)
    config.set(section1, "ACCESS_TOKEN", auth.access_token)
    config.set(section1, "ACCESS_SECRET", auth.access_token_secret)
    config.set(section1, "CONSUMER_KEY", CONSUMER_KEY)
    config.set(section1, "CONSUMER_SECRET", CONSUMER_SECRET)

    settingfile = os.path.join(os.path.dirname(__file__), 'setting.ini')
    with open(settingfile, "w") as file:
        config.write(file)

def meke_output(status, args):
    if 'RT @' not in status.full_text \
       and '#FGO販売' not in status.full_text \
       and "#FGO買取"  not in status.full_text:
        source = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
        if args.debug:
            print(source)
        report_items = make_data4tweet(status.full_text)
        image_items, error_dic = calc_iamge_diff(status, savelocal=args.savelocal, debug=args.debug)

        #差分結果部分
        report_diff = calc_diff(report_items, image_items, inverse=args.inverse)
        sum = 0
        for n in report_diff.values():
            sum = sum + abs(n)
        if sum == 0:
            if len(error_dic.keys()) > 0:
                print(source, end=",,")
                for error in error_dic.keys():
                    print(error, end=" ")
                    print(error_dic[error], end= ",")                
                print()
            return
        print(source, end=",")
        print (dic2str(report_diff), end=",")
        for error in error_dic.keys():
            print(error, end=" ")
            print(error_dic[error], end= ",")
        print()
    
def get_one_tweet(args, api):
    """
    ツイートを一つ処理する
    """
    tweet_pattern = "https://twitter.com/.+?/status/"
    tweet_id = re.sub(tweet_pattern, "", args.url)

    if not tweet_id.isdigit():
        print("URLが正しくありません")
        sys.exit(1)

    tweet_id = int(tweet_id)

    try:
        status = api.get_status(tweet_id, tweet_mode="extended")
    except:
        print("エラー: ツイート読み込みに失敗しました")
        sys.exit(1)

##    read_item()

    report_items = make_data4tweet(status.full_text)
    image_items, error_dic = calc_iamge_diff(status, savelocal=args.savelocal, debug=args.debug)

    #差分結果部分
    report_diff = calc_diff(report_items, image_items, args.inverse)
    print("【計算差分】", end="")
    print(dic2str(report_diff))

    if args.suppress == False:    
        print()
        #報告(文字)部分
        print("【周回報告】", end="")
        print(dic2str(report_items))

        #報告(画像)部分
        print("【画像差分】", end="")
        print (dic2str(image_items))
        for error in error_dic.keys():
            print(error, end=" ")
            print(error_dic[error], end= ",")
    
def get_tweet_auto(args, api, last_id):
    """
    検索で取得できる #FGO周回カウンタ　のツイートを全て処理する
    """
    status = None
    max_id = 0
    resume_id = last_id

    for loop in range(MAX_LOOP):
        if args.resume == True:
            for status in api.search(q='#FGO周回カウンタ',
                                     lang='ja',result_type='mixed',
                                     count=MAXSERCH,
                                     since_id=resume_id,
                                     max_id=max_id -1,
                                     tweet_mode="extended"):
                meke_output(status, args)
                # --resume　オプション用データ
                if int(last_id) < int(status.id):
                    last_id = int(status.id)               

        else:
            for status in api.search(q='#FGO周回カウンタ',
                                     lang='ja',result_type='mixed',
                                     count=MAXSERCH,
                                     max_id=max_id -1,
                                     tweet_mode="extended"):
                meke_output(status, args)
                # --resume　オプション用データ
                if int(last_id) < int(status.id):
                    last_id = int(status.id)               
        if status != None:
            max_id=status.id

    return last_id           
    
    
if __name__ == '__main__':
    last_id = -1
    settingfile = os.path.join(os.path.dirname(__file__), 'setting.ini')
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
    api = tweepy.API(auth)

    ## オプションの解析
    parser = argparse.ArgumentParser(description='周回カウンタのスクショ付き報告をチェック')
    # 3. parser.add_argumentで受け取る引数を追加していく
    parser.add_argument('-u', '--url', help='Tweet URL')    # 必須の引数を追加
    parser.add_argument('-a', '--auto', help='#FGO周回カウンタ ツイの自動取得で連増実行', action='store_true')     
    parser.add_argument('-s', '--suppress', help='差分のみ出力', action='store_true')     
    parser.add_argument('-i', '--inverse', help='差分計算を逆にする', action='store_true')     
    parser.add_argument('-r', '--resume', help='-a を前回実行した続きから出力', action='store_true')     
    parser.add_argument('-l', '--savelocal', help='画像ファイルをローカルに保存', action='store_true')     
    parser.add_argument('-d', '--debug', help='デバッグ情報を出力', action='store_true')     
    parser.add_argument('--version', action='version', version=progname + " " + version)

    args = parser.parse_args()    # 引数を解析

    if args.auto == True:
        last_id = get_tweet_auto(args, api, last_id)
               
        config.set(section0, "LAST_ID", str(last_id))
        with open("setting.ini", "w") as file:
            config.write(file)
        sys.exit(0)

    # ここから個別ツイート取得用ルーチン
    if args.url == None:
        parser.print_help()
    else:
        get_one_tweet(args, api)
        
