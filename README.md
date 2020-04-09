![fgosccalc1](https://user-images.githubusercontent.com/62515228/78868001-0ca71a80-7a7d-11ea-84b2-087f6b2466fc.png)
# fgosccalc
FGOのクエスト情報戦利品の周回前後のスクショを読み取り差分を計算

このプログラムをウェブ化したものをまっくすさんが公開しています https://fgosccalc.appspot.com/

## 必要なソフトウェア
Python 3.7以降

### 必要なPython ライブラリ
* opencv-python
* opencv-contrib-python

calctweet.py を使用する場合は以下のものが必要
* tweepy
* requests

## ファイル
1. img2str.py : コマンドプロンプトでファイルを読み込みアイテムを出力
2. fgosccalc.py　: コマンドプロンプトでファイル2つを読み込み差分を出力
3. fgosccalc.cgi : fgosccalc.py の CGI版
4. calctweet.py : 周回報告のTweet URL から周回報告と画像差分をチェックする
5. item.csv : calctweet.py で使用するアイテム標準化ファイル
6. setting-dst.ini calctweet.py で使用する setting.ini の元ファイル
7. makeprop.py : property.xml を作成する
8. data/* : 文字学習用データ property.xml 作成後は必要無い

以下は4.実行時に作成される
9. property.xml : 文字認識のためのトレーニングファイル

## インストール
必要な Python ライブラリをインストールする
makeprop.py を1度だけ実行

### calctweet.py のインストールは以下の手順が必要
1. setting-dst.ini をコピーして setting.ini を作成
2. consumer_key　と　consumer_secret を手に入れる
基本的に一般配布はしないので、https://developer.twitter.com/ からアプリケーション登録をして手に入れてください
ここでaccess_token と access_secret を入手すると4の手順がとばせます
3. setting.ini の次の行に取得したconsumer_key と　consumer_secretを入力する
consumer_key = 
consumer_secret = 
4. calctweet.py を起動するとブラウザが立ち上がり、アプリ連携画面になるのでアプリ連携し、表示された PIN を入力する

## 使い方
imgstr.py ファイル名

fgosccalc.py ファイル名 ファイル名

calctweet.py TweetURL
