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

progname = "FGOツイートスクショチェック"
version = "0.0.1"

##CONSUMER_KEY        = 'BOxfvMp2SVGffWdelzn8jBsPZ'
##CONSUMER_SECRET     = 'ycMSz4aI5RISlwNoG2uJ3ffZRyUoaWeIMxnoxMKAJ9P5DIkuCB'
##ACCESS_TOKEN_KEY    = '1077831827530833921-8AGihdrG0MUMJuCKg3plqffYyZXhJC'
##ACCESS_TOKEN_SECRET = 'hP9UuTdm3yu9DTy025LCidM3A006J8upW1zwYtYhd18gK'


sozai = {}
sozai_betsumei = {}

def read_item():
    """
    CSV形式のアイテム変換データを読み込む
    """
    itemfile = os.path.join(os.path.dirname(__file__), 'item.csv')
    with open(itemfile, 'r' , encoding="utf_8") as f:
        try:
            reader = csv.reader(f)
            header = next(reader)  # ヘッダーを読み飛ばしたい時

            for row in reader:
##                q = {}
                for item in row[2:]:
                    if item == "":
                        break
                    sozai_betsumei[item] = row[1]
                sozai[row[1]] = row[0]
        except UnicodeDecodeError:
            print("[エラー]item.csv の文字コードがおかしいようです。UTF-8で保存してください。")
            sys.exit()
        except IndexError:
            print("[エラー]item.csv がCSV形式でないようです。")
            sys.exit()

def normalize_item(s):
    for pattern in sozai_betsumei.keys():
        if re.match(pattern, s):
            s = re.sub("^" + s + "$", sozai_betsumei[pattern], s)
            break
    return s
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
        tmpitem = normalize_item(re.sub(pattern, r"\g<name>", item).strip())
        if " " in tmpitem:
            continue
        else:
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

def calc_iamge_diff(status):
    if not hasattr(status, 'extended_entities'):    
        return []

    if 'media' in status.extended_entities:
        # 思い処理なのでこのプログラム場合はエラー判定後に実行
        dropitems = img2str.DropItems()        
        svm = cv2.ml.SVM_load(str(img2str.training))

        itemlists = []
        for i, media in enumerate(status.extended_entities['media']):
            response = requests.get(media['media_url'] + ':orig')
            tmp = response.content
            img_buf = np.frombuffer(tmp, dtype='uint8')
            image = cv2.imdecode(img_buf, 1)
            sc = img2str.ScreenShot(image, svm, dropitems)
            itemlists.append(sc.itemlist)
        ## 通常素材が埋まって無い報告は無いと推測してそういう報告は無効と判断
            new_itemlists = []                    
            for itemlist in itemlists:
                for item in itemlist:
                    if item[0] in dropitems.dist_item.keys():
                        new_itemlists.append(itemlist)
                        break

    item_dic = {}
    #戦利品スクショでないものはスキップして new_listを作成
    if len(new_itemlists) >= 2:
        for before, after in zip(new_itemlists[0], new_itemlists[1]):
            if before[1].isdigit() and after[1].isdigit() and (not before[0].startswith("未ドロップ") and not after[0].startswith("未ドロップ")):
                item_dic[normalize_item(after[0])] = int(after[1])-int(before[1])

    # 報告前と報告後の後の画像順が逆の場合の対策
    sum = 0
    for n in item_dic.values():
        sum = sum + n
    if sum < 0:
        for item in item_dic:
            item_dic[item] = item_dic[item] * -1


#                new_list.append((after[0], int(after[1])-int(before[1])))

#    new_dict = dict(new_list)
    
##    twitter_url = "https://twitter.com/" + tweet.user.screen_name + "/status/" + str(status)
##    outresult = min(finalresult, key=key_func)
##    output = []
##    if result.endswith('-'):
##        output.append(twitter_url)
##        output.append(outresult[1][:-1])
##    else:
##        output.append(twitter_url)
##        output.append(outresult[1])
                   
    return item_dic

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

def calc_diff(report_dic, image_dic):
    result_dic = {}
    for item in report_dic.keys():
        if item in image_dic.keys():
            result_dic[item] = report_dic[item] - image_dic[item]
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
    
if __name__ == '__main__':
    settingfile = os.path.join(os.path.dirname(__file__), 'setting.ini')
    config = configparser.ConfigParser()
    try:
        config.read(settingfile)
        section1 = "auth_info"
        ACCESS_TOKEN = config.get(section1, "ACCESS_TOKEN")
        ACCESS_SECRET = config.get(section1, "ACCESS_SECRET")
        CONSUMER_KEY = config.get(section1, "CONSUMER_KEY")
        CONSUMER_SECRET = config.get(section1, "CONSUMER_SECRET")
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
    parser.add_argument('tweet_url', help='Tweet URL', nargs='*')    # 必須の引数を追加
    parser.add_argument('-s', '--suppress', help='差分のみ出力', action='store_true')     
    parser.add_argument('--version', action='version', version=progname + " " + version)

    args = parser.parse_args()    # 引数を解析

    tweet_pattern = "https://twitter.com/.+?/status/"
    tweet_id = re.sub(tweet_pattern, "", args.tweet_url[0])

    if not tweet_id.isdigit():
        print("URLが正しくありません")
        sys.exit(1)

    tweet_id = int(tweet_id)

    try:
        status = api.get_status(tweet_id, tweet_mode="extended")
    except:
        print("エラー: ツイート読み込みに失敗しました")
        sys.exit(1)


    read_item()

    report_items = make_data4tweet(status.full_text)
    image_items = calc_iamge_diff(status)

    #差分結果部分
    report_diff = calc_diff(report_items, image_items)
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
