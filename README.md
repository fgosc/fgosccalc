# fgosccalc
FGOのクエスト情報戦利品の周回前後のスクショを読み取り差分を計算

## 必要なソフトウェア
Python 3.7以降

## 必要なライブラリ
OpenCV

## ファイル
1. img2str.py : コマンドプロンプトでファイルを読み込みアイテムを出力
2. fgosccalc.py　: コマンドプロンプトでファイル2つを読み込み差分を出力
3. fgosccalc.cgi : fgosccalc.py の CGI版
4. makeprop.py : property.xml を作成する
5. data/* : 文字学習用データ

以下は4.実行時に作成される
6. property.xml : 文字認識のためのトレーニングファイル

## インストール
OpenCV をインストールする

makeprop.py を1度だけ実行

## 使い方
imgstr.py ファイル名

fgosccalc.py ファイル名 ファイル名
