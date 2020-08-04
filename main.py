import copy
import io
import base64
import json
import logging
from pathlib import Path
from urllib.parse import quote_plus

import cv2
import numpy as np
from bottle import Bottle, redirect, request, template

import img2str
import fgosccalc
from storage.filesystem import FileSystemStorage
from storage.datastore import GoogleDatastoreStorage

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
app = Bottle()


if __name__ == "__main__":
    # local
    logger.info('use FileSystemStorage')
    storage = FileSystemStorage(Path(__file__).resolve().parent / Path("item/"))
else:
    # appengine
    # TODO テストと本番で Entity を分けたい。設定ファイルで切り替えるか？
    logger.info('use GoogleDatastoreStorage: kind=Item')
    storage = GoogleDatastoreStorage('Item')


def get_np_array(stream):
    return np.asarray(bytearray(stream.read()), dtype=np.uint8)


def makeup(result_list):
    return '-'.join(['{}{}'.format(item["name"], item["dropnum"]) for item in result_list])


def is_valid_file(obj):
    if obj is None:
        logger.warning('file1 is None')
        return False
    if obj.file is None:
        logger.warning('file is not specified')
        return False
    f = obj.file
    f.seek(0, io.SEEK_END)
    if f.tell() == 0:
        logger.warning('blank file')
        return False
    f.seek(0)
    return True


@app.get('/upload')
def upload_get():
    redirect('/')


@app.post('/upload')
def upload_post():
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')

    logger.info('test file1')
    if not is_valid_file(file1):
        redirect('/')

    logger.info('test file2')
    if not is_valid_file(file2):
        redirect('/')

    dropitems = img2str.DropItems(storage=storage)

    svm = cv2.ml.SVM_load(str(img2str.training))

    im1 = cv2.imdecode(get_np_array(file1.file), 1)
    sc1 = img2str.ScreenShot(im1, svm, dropitems)

    im2 = cv2.imdecode(get_np_array(file2.file), 1)
    sc2 = img2str.ScreenShot(im2, svm, dropitems)

    logger.info('sc1: %s', sc1.itemlist)
    logger.info('sc2: %s', sc2.itemlist)

    result_list = fgosccalc.make_diff(copy.deepcopy(sc1.itemlist), copy.deepcopy(sc2.itemlist))
    logger.info('result_list: %s', result_list)

    questname, questdrop = fgosccalc.get_questinfo(sc1, sc2)
    logger.info('quest: %s', questname)
    logger.info('questdrop: %s', questdrop)

    drops_diff = fgosccalc.DropsDiff(result_list, questname, questdrop)
    parsed_obj = drops_diff.parse(dropitems)

    dropdata = parsed_obj.as_json_data()
    logger.info('dropdata json: %s', dropdata)

    # さらに web 向けに加工する
    for d in dropdata:
        d['order'] = d['id']
        d['initial'] = d['report']
        d['add'] = 0
        d['reduce'] = 0

    before_after_pairs = make_before_after_pairs(sc1.itemlist, sc2.itemlist)
    logger.info('pairs: %s', before_after_pairs)
    contains_unknown_items = any([pair[0].startswith('item0') for pair in before_after_pairs])

    ok, jpg1 = nparray_to_image(im1)
    if ok:
        before_im = base64.b64encode(jpg1.tobytes())
    else:
        before_im = None

    ok, jpg2 = nparray_to_image(im2)
    if ok:
        after_im = base64.b64encode(jpg2.tobytes())
    else:
        after_im = None

    return template('result',
        result=makeup(result_list),
        sc1_available=(len(sc1.itemlist) > 0),
        sc2_available=(len(sc2.itemlist) > 0),
        before_after_pairs=before_after_pairs,
        before_im=before_im,
        after_im=after_im,
        questname=questname,
        dropdata=json.dumps(dropdata),
        contains_unknown_items=contains_unknown_items,
    )


def nparray_to_image(im):
    h, _ = im.shape[:2]
    # 解像度の高いものは半分にリサイズ
    if h >= 1000:
        resized_im = cv2.resize(im, dsize=None, fx=0.5, fy=0.5)
    else:
        resized_im = im
    return cv2.imencode('.jpg', resized_im)


def make_before_after_pairs(before_list, after_list):
    pairs = []
    for before, after in zip(before_list, after_list):
        if before["id"] == img2str.ID_NO_POSESSION or after["id"] == img2str.ID_NO_POSESSION:
            continue
        if not str(before["dropnum"]).isdigit() or not str(after["dropnum"]).isdigit():
            continue
        if before["id"] != after["id"]:
            continue
        pair = (before["name"], before["dropnum"], after["dropnum"], after["dropnum"] - before["dropnum"])
        pairs.append(pair)
    return pairs


@app.get('/items')
def items_get():
    d = storage.known_item_dict()
    dcopy = {}
    for k in d:
        success, im = cv2.imencode('.png', d[k])
        if not success:
            dcopy[k] = None
            continue
        dcopy[k] = base64.b64encode(im.tobytes())
    return template('items', items=dcopy)


if __name__ == "__main__":
    # appengine 上では / アクセスのときは static な index.html
    # を返すので handler は不要だが、ローカルで動かす場合は必要。
    import os
    from bottle import get, route, static_file

    static_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    @app.get('/')
    def index():
        return static_file('index.html', root=static_root)

    @app.route('/static/<filepath:path>')
    def static_content(filepath):
        return static_file(filepath, root=static_root)
    
    app.run(host='localhost', port=8080, debug=True)
