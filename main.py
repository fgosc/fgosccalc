import base64
import logging
from pathlib import Path

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


def makeup(result_dict):
    return '-'.join(['{}{}'.format(k, v) for k, v in result_dict.items()])


@app.get('/upload')
def upload_get():
    redirect('/')


@app.post('/upload')
def upload_post():
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')

    if file1 is None or file2 is None:
        redirect('/')

    dropitems = img2str.DropItems(storage=storage)

    svm = cv2.ml.SVM_load(str(img2str.training))

    im1 = cv2.imdecode(get_np_array(file1.file), 1)
    sc1 = img2str.ScreenShot(im1, svm, dropitems)

    im2 = cv2.imdecode(get_np_array(file2.file), 1)
    sc2 = img2str.ScreenShot(im2, svm, dropitems)

    logger.info('sc1: %s', sc1.itemlist)
    logger.info('sc2: %s', sc2.itemlist)

    result_dict = fgosccalc.make_diff(sc1.itemlist, sc2.itemlist)
    logger.info('result_dict: %s', result_dict)
    before_after_pairs = make_before_after_pairs(sc1.itemlist, sc2.itemlist)

    ok, png1 = cv2.imencode('.png', im1)
    if ok:
        before_im = base64.b64encode(png1.tobytes())
    ok, png2 = cv2.imencode('.png', im2)
    if ok:
        after_im = base64.b64encode(png2.tobytes())

    return template('result',
        result=makeup(result_dict),
        before_after_pairs=before_after_pairs,
        before_im=before_im,
        after_im=after_im,
    )


def make_before_after_pairs(before_list, after_list):
    pairs = []
    for pair in zip(before_list, after_list):
        name_before, num_before = pair[0]
        name_after, num_after = pair[1]
        if name_before.startswith('未ドロップ') or name_before.startswith('泥無しアイテム'):
            continue
        if not num_before.isdigit() or not num_after.isdigit():
            continue
        if name_before != name_after:
            continue
        pairs.append((name_before, num_before, num_after, int(num_after) - int(num_before)))
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

    @app.route('/static/<filepath>')
    def static_content(filepath):
        return static_file(filepath, root=static_root)
    
    app.run(host='localhost', port=8080, debug=True)
