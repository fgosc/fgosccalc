![fgosccalc1](https://user-images.githubusercontent.com/62515228/78868001-0ca71a80-7a7d-11ea-84b2-087f6b2466fc.png)
# fgosccalc
FGOのクエスト情報戦利品の周回前後のスクショを読み取り差分を計算

このプログラムをウェブ化したものをまっくすさんが公開しています https://fgosccalc.appspot.com/

## 必要なソフトウェア
Python 3.7以降

## ファイル
- img2str.py : コマンドプロンプトでファイルを読み込みアイテムを出力
  - makeprop.py : img2str.py で使用するproperty.xml を作成する
    - data/* : 文字学習用データ
  - freequest.csv : クエスト名自動認識に使用される
  - syurenquest.csv :  クエスト名自動認識に使用される
  - syoji_silber.png : 「所持」の文字位置を認識するためのファイル
  - hash_ce.csv : 概念礼装画像認識のためのデータファイル update.py で更新
  - hash_item.csv : アイテム画像認識のためのデータファイル update.py で更新
- fgosccalc.py　: コマンドプロンプトでファイル2つを読み込み差分を出力
  - item_nickname.csv : アイテムを短縮名に変換するためのデータ
- fgosccalc.cgi : fgosccalc.py の CGI版
- calctweet.py : 周回報告のTweet URL から周回報告と画像差分をチェックする
  - item.csv : calctweet.py で使用するアイテム標準化ファイル
  - setting-dst.ini  : calctweet.py で使用する setting.ini の元ファイル
- update.py : アイテムデータのアップデートを行う
  - std_item_nickname.csv : 恒常アイテムを短縮名に変換するためのデータ
  - ce_bl.txt : データ取得対象外の非ドロップ概念礼装のブラックリスト
  - item_bl.txt : データ取得対象外の非ドロップアイテムのブラックリスト

以下はmakeprop.py実行時に作成される
- property.xml : 文字認識のためのトレーニングファイル

## インストール
必要な Python ライブラリをインストールする

```
pip install -r requirements.txt`
```

fgoscdata を使えるようにする
```
$ git submodule update --init
```

makeprop.py を1度だけ実行

```
$ python makeprop.py
```

### calctweet.py のインストールは以下の手順が必要
1. setting-dst.ini をコピーして setting.ini を作成
2. consumer_key　と　consumer_secret を手に入れる  
基本的に一般配布はしないので、https://developer.twitter.com/ からアプリケーション登録をして手に入れる  
※ここでaccess_token と access_secret を入手すると4の手順がとばせます
3. setting.ini に取得したconsumer_key と consumer_secretを入力する  
次のように入力します  

```
 consumer_key = 入手したconsumer_key  
 consumer_secret = 入手したconsumer_secret
```
4. calctweet.py を起動するとブラウザが立ち上がり、アプリ連携画面になるのでアプリ連携し、表示された PIN を入力する

## 使い方
### img2str.py
```
usage: img2str.py [-h] [-d] [--version] file

戦利品画像を読み取る

positional arguments:
  file         FGOの戦利品スクショ

optional arguments:
  -h, --help   show this help message and exit
  -d, --debug  デバッグ情報を出力
  --version    show program's version number and exit
```

### fgosccalc.py
周回前後二枚の戦利品スクショのドロップ差分を計算する
```
usage: fgosccalc.py [-h] [--loglevel {DEBUG,INFO,WARNING}] [--output OUTPUT]
                    [--future]
                    sc1 sc2

positional arguments:
  sc1                   1st screenshot
  sc2                   2nd screenshot

optional arguments:
  -h, --help            show this help message and exit
  --loglevel {DEBUG,INFO,WARNING}
                        loglevel [default: INFO]
  --output OUTPUT       output file [default: STDOUT]
  --future
```
### calctweet.py
```
usage: calctweet.py [-h] [-u URL] [-a] [-s] [-i] [-r] [-l] [-d] [--version]

周回カウンタのスクショ付き報告をチェック

optional arguments:
  -h, --help         show this help message and exit
  -u URL, --url URL  Tweet URL
  -a, --auto         #FGO周回カウンタ ツイの自動取得で連増実行
  -s, --suppress     差分のみ出力
  -i, --inverse      差分計算を逆にする
  -r, --resume       -a を前回実行した続きから出力
  -l, --savelocal    画像ファイルをローカルに保存
  -d, --debug        デバッグ情報を出力
  --version          show program's version number and exit
 ```

## 制限
* 8桁の所持数には対応していない
* 縮小を行ったスクリーンショットではアイテムと文字の認識率が悪くなる。目安としては額縁を抜いて横サイズ1200以下に縮小を行うと著しく認識率が落ちる
* トリミングを行った画像にも対応しているが、「エネミー」タブと「閉じる」ボタンが入っていないものには対応していない。また、右上の特異点表記を入れないと周回場所の自動認識には対応しない
* 周回場所の自動認識で誤認識されるクエストがある
  * 未確認座標X-Bを未確認座標X-Cに
  * セプテム ローマをセプテムメディオラヌムに
