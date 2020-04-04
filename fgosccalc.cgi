#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cgi
import io
import sys
import os
import numpy as np
import cv2
import img2str
import fgoscdiff

if __name__ == '__main__':

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print('Content-Type: text/html; charset=UTF-8\n')
    html_body = """
<!DOCTYPE html>
<html>
<head>
<title>FGOスクショ差分計算機</title>
</head>
<body>
<h1>FGOスクショ差分チェッカー</h1>
<p>
クエスト情報の戦利品のスクショを周回前後の2枚投稿すると、アイテム獲得数を計算します
</p>
<p>%s</p>
<form method="post" action="fgoscdiff2.cgi" enctype="multipart/form-data">
<p><input type="file" name="file1" size="30"></p>
<p><input type="file" name="file2" size="30"></p>
<p><input type="submit" value="送信する"></p>
</form>

</body>"""

    try:
        import msvcrt
        msvcrt.setmode(0, os.O_BINARY)
        msvcrt.setmode(1, os.O_BINARY)
    except ImportError:
        pass

##    print(html_body)
    result = ''
    result1 = ''
    result2 = ''
##    print (html_body % result)
    form = cgi.FieldStorage()
    dropitems = img2str.DropItems()        
    svm = cv2.ml.SVM_load(str(img2str.training))
    if 'file1' in form.keys() and 'file2' in form.keys():
        item1 = form['file1']
        img_buf1 = np.frombuffer(item1.file.read(), dtype='uint8')
        image1 = cv2.imdecode(img_buf1, 1)
        sc1 = img2str.ScreenShot(image1, svm, dropitems)
        result1 = sc1.itemlist

        item2 = form['file2']
        img_buf2 = np.frombuffer(item2.file.read(), dtype='uint8')
        image2 = cv2.imdecode(img_buf2, 1)
        sc2 = img2str.ScreenShot(image2, svm, dropitems)
        result2 = sc2.itemlist
        new_list = fgoscdiff.make_diff(sc1.itemlist, sc2.itemlist)
        for item in new_list:
            result = result + item[0] + str(item[1]) + '-'
        if len(result) > 0:
            result = result[:-1]

    print (html_body % (result))