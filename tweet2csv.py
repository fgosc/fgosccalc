import io
import sys
from pathlib import Path
import re
import json
from typing import List, Dict
import subprocess
import csv

import PySimpleGUI as sg
import requests
import numpy as np
import cv2
import git

from lib.twitter import set_twitter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sg.theme('DarkAmber')   # デザインテーマの設定

URL_BASIC_WAR = "https://api.atlasacademy.io/export/JP/basic_war.json"
URL_BASIC_CE = "https://api.atlasacademy.io/export/JP/basic_equip.json"
URL_BASIC_ITEM = "https://api.atlasacademy.io/export/JP/nice_item.json"
URL_WAR = "https://api.atlasacademy.io/nice/JP/war/"

BASEDIR = Path(__file__).resolve().parent
FGOSCDATADIR = Path(__file__).resolve().parent / Path("fgoscdata")
DATADIR = BASEDIR / Path("../FGOData")
FILE_QUEASTINFO = DATADIR / Path("JP_tables/quest/viewQuestInfo.json")
CSVDIR = BASEDIR / Path("fgoscdata/data/csv")
JSONDIR = BASEDIR / Path("fgoscdata/data/json")
OK = 0
ERROR = -1
Image_dir = Path(__file__).resolve().parent / Path("image/")
repo = git.Repo(BASEDIR)
repo_sub = git.Repo(FGOSCDATADIR)


def open_file_with_utf8(filename):
    '''utf-8 のファイルを BOM ありかどうかを自動判定して読み込む
    '''
    is_with_bom = is_utf8_file_with_bom(filename)

    encoding = 'utf-8-sig' if is_with_bom else 'utf-8'

    return open(filename, encoding=encoding)


def is_utf8_file_with_bom(filename):
    '''utf-8 ファイルが BOM ありかどうかを判定する
    '''
    line_first = open(filename, encoding='utf-8').readline()
    return (line_first[0] == '\ufeff')


def make_ce_list():
    r_get = requests.get(URL_BASIC_CE)
    ces = r_get.json()
    ce_list = [ce["name"] for ce in ces]
    new_list = ce_list[::-1]
    return new_list[:15]


def make_drop_item_list():
    drop_item_list = ["QP",
                      "剣猛火", "剣業火",
                      "槍猛火", "槍業火",
                      "弓猛火", "弓業火",
                      "騎猛火", "騎業火",
                      "術猛火", "術業火",
                      "殺猛火", "殺業火",
                      "狂猛火", "狂業火",
                      ]
    r_get = requests.get(URL_BASIC_ITEM)
    items = r_get.json()
    item_list = [item["name"] for item in items
                 if item["name"] != "サーヴァントコイン"
                 and not item["name"].startswith("秘密の地図")]
    drop_item_list += item_list[::-1]
    return drop_item_list


def extract_war() -> Dict[int, str]:
    """mstWar.json から最新のイベントを抽出する

    Returns:
        Dict[int, str]: eventId と イベント名
    """
    r_get = requests.get(URL_BASIC_WAR)
    wars = r_get.json()
    # eventId でソート
    wars_sorted = sorted(wars, key=lambda x: x['eventId'], reverse=True)
    war = wars_sorted[0]
    return {"id": war["id"], "name": war["name"]}


def make_fq_list(eventId: int) -> List[Dict[int, str]]:
    """最新のイベントからフリークエストのみを抽出する

    Args:
        eventId (int): [description]

    Returns:
        List[Dict[int, str]]: [description]
    """
    r_get = requests.get(URL_WAR + str(eventId))
    war = r_get.json()
    json_open = open(FILE_QUEASTINFO, 'r')
    questInfo = json.load(json_open)
    freeQuestId = [quest["questId"] for quest in questInfo]
    fq_list = []
    for spot in war["spots"]:
        for quest in spot["quests"]:
            if quest["id"] in freeQuestId:
                if "【高難易度】" in quest["name"]:
                    continue
                fq_list.append({"id": quest["id"], "name": quest["name"]})
    fq_list_sorted = sorted(fq_list, key=lambda x: x["id"], reverse=True)
    return fq_list_sorted


def input_validation(values: Dict) -> int:
    if values["twitter1"] == "":
        sg.popup_error('Twitter URL を入力してください')
        print('Twitter URL を入力してください')
        return ERROR
    # Twitter URL形式が不正
    tweet_pattern = "https://twitter.com/.+?/status/"
    tweet_id = re.sub(tweet_pattern, "", values["twitter1"])
    if not tweet_id.isdigit():
        sg.popup_error('Twitter URL が正しい形式ではありません')
        print('Twitter URL が正しい形式ではありません')
        return ERROR
    if values["file1"] == "":
        sg.popup_error('出力CSV を入力してください')
        print('出力CSV を入力してください')
        return ERROR
    return OK


def get_image(questId: int, tweetId: int) -> int:
    api = set_twitter()
    status = api.get_status(tweetId, tweet_mode="extended")
    if "extended_entities" not in dir(status):
        sg.popup_error("添付ファイルが無いツイートが指定されています")
        print("添付ファイルが無いツイートが指定されています", flush=True)
        return ERROR
    if 'media' in status.extended_entities:
        for i, media in enumerate(status.extended_entities['media']):
            response = requests.get(media['media_url'] + ':orig')
            if response.status_code != requests.codes.ok:
                url = media['media_url'].replace(".jpg", "") \
                      + "?format=jpg&name=4096x4096"
                response = requests.get(url)
                if response.status_code != requests.codes.ok:
                    print("image" + str(i + 1) + str(response.status_code))
                    break
            tmp = response.content
            img_buf = np.frombuffer(tmp, dtype='uint8')
            image = cv2.imdecode(img_buf, 1)
            if i == 0:
                Image_file = Image_dir / Path(str(questId) + ".jpg")
            else:
                Image_file = Image_dir / Path(str(questId)
                                              + "_" + str(i) + ".jpg")
            if not Image_dir.is_dir():
                Image_dir.mkdir()
            cv2.imwrite(str(Image_file), image)
            print("%sを書き込みしました" % str(Image_file))
    return OK


def main():
    DEBUG = False
    # イベント抽出
    war = extract_war()
    # イベントからフリークエストリスト作成
    quests_list = make_fq_list(war["id"])
    quests = [quest["name"] for quest in quests_list]
    ce_list = make_ce_list()
    drop_item_list = make_drop_item_list()
    # ウィンドウに配置するコンポーネント
    layout = [[sg.Text('イベント:' + war["name"])],
              [sg.Listbox(quests,
                          default_values=[quests_list[0]["name"]],
                          size=(60, 5),
                          key="quest1")],
              [sg.Text('Twitter URL:'),
               sg.InputText(size=(80, 1),
               key="twitter1")],
              [sg.Text('出力CSV:'),
               sg.InputText(size=(80, 1), key="file1"),
               sg.FileBrowse(file_types=(("CSVファイル", "*.csv"),)),
               sg.Button('新規作成', key="newfile1")],
              [sg.Button('実行',
                         button_color=('#0000ff', '#ff0000'),
                         key="submit1")],
              [sg.Text('ログ:')]]
    if DEBUG is False:
        layout.append([sg.Output(size=(130, 20))])

    # ウィンドウの生成
    window = sg.Window('クエスト名認識作業自動化', layout)

    # イベントループ
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == 'newfile1':
            new_filename = sg.popup_get_text('作成するファイル名',
                                             title="ファイル新規作成",
                                             default_text='.csv')
            print(new_filename)
            if not new_filename.endswith(".csv"):
                sg.popup_error('拡張子は.csvのみが有効です:' + new_filename)
                print('拡張子は.csvのみが有効です:' + new_filename)
            elif new_filename != ".csv":
                if (CSVDIR / Path(new_filename)).exists():
                    sg.popup_error('すでに存在するファイルです:' + new_filename)
                    continue
                else:
                    window["file1"].update(str(CSVDIR / Path(new_filename)))
            else:
                sg.popup_error('.csvの前に文字を入力してください')
                print('.csvの前に文字を入力してください')
            continue
        if event == 'submit1':
            print("親リポジトリ更新")
            print(repo.git.pull('origin', 'master'))
            print("submodule 更新")
            print(repo_sub.git.checkout('master'))
            print(repo_sub.git.pull('origin', 'master'))
            # validation
            if input_validation(values) != OK:
                continue
            # twitterから画像を取得
            questId = [quest["id"] for quest in quests_list
                       if quest["name"] == values["quest1"][0]][0]
            print("questId: %d" % questId)
            tweet_pattern = "https://twitter.com/.+?/status/"
            tweetId = re.sub(tweet_pattern, "", values["twitter1"])
            tweetId = int(tweetId)
            print("tweetId: %d" % tweetId)
            if get_image(questId, tweetId) != OK:
                continue
            # img2str.py の実行
            cp = subprocess.run(['python', 'img2str.py',  '--csv',
                                 str(Image_dir / (str(questId) + ".jpg"))],
                                encoding='cp932',
                                stdout=subprocess.PIPE)
            if cp.returncode != OK:
                sg.popup_error('img2str.py がエラーを返しました。ほとんどは画像が戦利品のスクリーンショットでない場合です。')
                print('img2str.py がエラーを返しました。ほとんどは画像が戦利品のスクリーンショットでない場合です。', flush=True)
                continue
            print(cp.stdout)
            item_list = cp.stdout.strip().split(',')
            file1 = values["file1"]
            # クエスト名修正
            quest_short_name = sg.popup_get_text('クエスト「%s」の短縮名に変更がある場合は修正してください' % item_list[1],
                                                 title="クエスト短縮名修正",
                                                 default_text=item_list[2])
            # キャンセルの場合
            if quest_short_name is None:
                print("キャンセルされました", flush=True)
                continue
            print("クエスト短縮名: %s" % quest_short_name)
            item_list[2] = quest_short_name
            print(item_list)
            # 未ドロップ修正
            for i, item in enumerate(item_list):
                if i < 3:
                    continue
                if item == "未ドロップ":
                    event, values = sg.Window('未ドロップの概念礼装選択',
                                              layout=[[sg.Text("%d枠目にある未ドロップの概念礼装を選択してください" % (i - 2))],
                                                      [sg.Listbox(ce_list, key='_LIST_',
                                                                  size=(max([len(str(v)) for v in ce_list]) + 20,
                                                                        len(ce_list)),
                                                                  select_mode='extended',
                                                                  bind_return_key=True),
                                                       sg.OK()]]).read(close=True)
                    chosen = values['_LIST_'] if event is not None else None
                    item_list[i] = chosen[0]
            # 未ドロップ修正
            for i, item in enumerate(item_list):
                if i < 3:
                    continue
                if item == "所持数無しアイテム":
                    event, values = sg.Window('所持数無しアイテム選択',
                                              layout=[[sg.Text("%d枠目にある所持数無しアイテムを選択してください" % (i - 2))],
                                                      [sg.Listbox(drop_item_list, key='_LIST_',
                                                                  size=(max([len(str(v)) for v in drop_item_list]) + 20,
                                                                        15),
                                                                  select_mode='extended',
                                                                  bind_return_key=True),
                                                       sg.OK()]]).read(close=True)
                    chosen = values['_LIST_'] if event is not None else None
                    if chosen[0] == "QP":
                        item_list[i] = ""
                    else:
                        item_list[i] = chosen[0]
            print(item_list)
            # CSVに追記
            print(values)
            header = ['id', 'quest', 'shortname',
                      'item01', 'item02', 'item03', 'item04', 'item05',
                      'item06', 'item07', 'item08', 'item09', 'item10',
                      'item11', 'item12', 'item13', 'item14', 'item15',
                      'item16']
            new_list = []
            if Path(file1).exists():
                with open_file_with_utf8(file1) as f:
                    reader = csv.reader(f)
                    for i, row in enumerate(reader):
                        if i > 0:
                            if int(row[0]) != questId:
                                new_list.append(row)
                            else:
                                new_list.append(item_list)
                new_list.sort()
            else:
                new_list.append(item_list)
            with open(file1, "w", encoding='utf_8_sig', newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                for row in new_list:
                    writer.writerow(row)
                print("CSVファイルへの書き込みが終了しました")
            # make_event_quest.py の実行
            cp = subprocess.run(['python',
                                 'fgoscdata/make_event_quest.py',
                                 file1],
                                stdout=subprocess.PIPE)
            if cp.returncode != OK:
                sg.popup_error('make_event_quest.py がエラーを返しました。処理を終了します。')
                print('make_event_quest.py がエラーを返しました。処理を終了します。', flush=True)
                continue
            print("JSONファイルへの変換が終了しました")
            repo_sub.git.add(file1)
            jsonfile = JSONDIR / Path(Path(file1).stem + '.json')
            print(jsonfile)
            repo_sub.git.add(jsonfile)
            # git commit
            repo_sub.index.commit('update ' + Path(file1).stem)
            # git push
            origin = repo_sub.remote(name="origin")
            origin.push()
            sg.popup("リモートリポジトリへの反映処理が終了しました")
            print("リモートリポジトリへの反映処理が終了しました")
    window.close()


if __name__ == '__main__':
    main()
