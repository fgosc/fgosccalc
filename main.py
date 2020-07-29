import io
import base64
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


def is_valid_file(f):
    if f is None:
        logger.warning('file is not specified')
        return False
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
    if not is_valid_file(file1.file):
        redirect('/')

    logger.info('test file2')
    if not is_valid_file(file2.file):
        redirect('/')

    dropitems = img2str.DropItems(storage=storage)

    svm = cv2.ml.SVM_load(str(img2str.training))

    im1 = cv2.imdecode(get_np_array(file1.file), 1)
    sc1 = img2str.ScreenShot(im1, svm, dropitems)

    im2 = cv2.imdecode(get_np_array(file2.file), 1)
    sc2 = img2str.ScreenShot(im2, svm, dropitems)

    logger.info('sc1: %s', sc1.itemlist)
    logger.info('sc2: %s', sc2.itemlist)

    result_list = fgosccalc.make_diff(sc1.itemlist, sc2.itemlist)
    logger.info('result_list: %s', result_list)

    questname, questdrop = fgosccalc.get_questinfo(sc1, sc2)
    logger.info('quest: %s', questname)
    logger.info('questdrop: %s', questdrop)

    drops_diff = fgosccalc.DropsDiff(result_list, questname, questdrop)
    parsed_obj = drops_diff.parse()
    formatted_output = parsed_obj.as_syukai_counter()

    before_after_pairs = make_before_after_pairs(sc1.itemlist, sc2.itemlist)

    ok, png1 = cv2.imencode('.png', im1)
    if ok:
        before_im = base64.b64encode(png1.tobytes())
    else:
        before_im = None

    ok, png2 = cv2.imencode('.png', im2)
    if ok:
        after_im = base64.b64encode(png2.tobytes())
    else:
        after_im = None

    return template('result',
        result=makeup(result_list),
        sc1_available=(len(sc1.itemlist) > 0),
        sc2_available=(len(sc2.itemlist) > 0),
        before_after_pairs=before_after_pairs,
        before_im=before_im,
        after_im=after_im,
        formatted_output=formatted_output,
        quoted_output=quote_plus(formatted_output),
    )


def make_before_after_pairs(before_list, after_list):
    pairs = []
    for before, after in zip(before_list, after_list):
##    for pair in zip(before_list, after_list):
##        name_before, num_before = pair[0]
##        name_after, num_after = pair[1]
        if before["id"] == -2 or after["id"] == -2:
            continue
        if not str(before["dropnum"]).isdigit() or not str(after["dropnum"]).isdigit():
            continue
        if before["id"] != after["id"]:
            continue
        pairs.append((before["name"], before["dropnum"], after["dropnum"], after["dropnum"] - before["dropnum"]))
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
