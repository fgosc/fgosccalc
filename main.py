#!/usr/bin/env python3
import argparse
import copy
import io
import base64
import json
import logging
from pathlib import Path

import cv2
import numpy as np
from bottle import Bottle, redirect, request, template

import dropitemseditor
import img2str
from storage.filesystem import FileSystemStorage
from storage.datastore import GoogleDatastoreStorage
from lib.twitter import upload_webfile

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
    file1 = request.files.getall('file1')
    file2 = request.files.getall('file2')
    extra1 = request.files.get('extra1')
    extra2 = request.files.get('extra2')

    owned_files = []
    if is_valid_file(extra1):
        logger.info('extra file1 found')
        owned_files.append(extra1.file)
    if is_valid_file(extra2):
        logger.info('extra file2 found')
        owned_files.append(extra2.file)

    dropitems = img2str.DropItems(storage=storage)

    svm = cv2.ml.SVM_load(str(img2str.training))

    sc_before = []
    im1 = []
    for i, f in enumerate(file1):
        logger.info('test file1-%s', i)
        if not is_valid_file(f):
            redirect('/')
        im1.append(cv2.imdecode(get_np_array(f.file), 1))
        sc_before.append(img2str.ScreenShot(im1[i], svm, dropitems))
    sc1 = dropitemseditor.merge_sc(sc_before)

    sc_after = []
    im2 = []
    for i, f in enumerate(file2):
        logger.info('test file2-%s', i)
        if not is_valid_file(f):
            redirect('/')
        im2.append(cv2.imdecode(get_np_array(f.file), 1))
        sc_after.append(img2str.ScreenShot(im2[i], svm, dropitems))
    sc2 = dropitemseditor.merge_sc(sc_after)

    logger.info('sc1: %s', sc1.itemlist)
    logger.info('sc2: %s', sc2.itemlist)

    if owned_files:
        _, owned_list = dropitemseditor.read_owned_ss(owned_files, dropitems, svm)
        logger.info('owned list: %s', owned_list)
        owned_diff = dropitemseditor.make_owned_diff(sc1.itemlist, sc2.itemlist, owned_list)
        logger.info('owned diff: %s', owned_diff)
    else:
        owned_diff = []

    result_list = dropitemseditor.make_diff(
        copy.deepcopy(sc1.itemlist),
        copy.deepcopy(sc2.itemlist),
        owned=owned_diff,
    )
    logger.info('result_list: %s', result_list)

    questname, questdrop = dropitemseditor.get_questinfo(sc1, sc2)
    logger.info('quest: %s', questname)
    logger.info('questdrop: %s', questdrop)

    drops_diff = dropitemseditor.DropsDiff(result_list, questname, questdrop)
    parsed_obj = drops_diff.parse(dropitems)

    dropdata = parsed_obj.as_json_data()
    logger.info('dropdata json: %s', dropdata)

    # さらに web 向けに加工する
    for d in dropdata:
        d['order'] = d['id']
        d['initial'] = d['report']
        d['add'] = 0
        d['reduce'] = 0

    before_after_pairs = make_before_after_pairs(sc1.itemlist, sc2.itemlist, owned_diff)
    logger.info('pairs: %s', before_after_pairs)
    contains_unknown_items = any([pair[0].startswith('item0') for pair in before_after_pairs])

    before_im = nparray_to_imagebytes(im1[0])
    after_im = nparray_to_imagebytes(im2[0])
    has_2nd_im = False
    before_2nd_im = None
    after_2nd_im = None
    if len(im1) > 1:
        has_2nd_im = True
        before_2nd_im = nparray_to_imagebytes(im1[1])
        after_2nd_im = nparray_to_imagebytes(im2[1])
    has_extra_im = False
    extra1_im = None
    extra2_im = None
    if len(owned_files) > 0:
        has_extra_im = True
        f = owned_files[0]
        # dropitemseditor.read_owned_ss() で終端まで読み取り済みなので
        # seek 位置を先頭に戻してやらないと imdecode できない。
        f.seek(0)
        extra1_nparray = cv2.imdecode(get_np_array(f), 1)
        extra1_im = nparray_to_imagebytes(extra1_nparray)
    if len(owned_files) > 1:
        f = owned_files[1]
        # 上記と同じ理由で seek(0) が必要。
        f.seek(0)
        extra2_nparray = cv2.imdecode(get_np_array(f), 1)
        extra2_im = nparray_to_imagebytes(extra2_nparray)
    owneds = []
    if extra1_im is not None:
        owned.apend(extra1_im)
        if extra2_im is not None:
            owned.apend(extra2_im)
#    image_url = upload_webfile(im1, im2, owneds)
    image_url = '[test str]'
    logger.info('url: %s', image_url)

    return template('result',
        result=makeup(result_list),
        sc1_available=(len(sc1.itemlist) > 0),
        sc2_available=(len(sc2.itemlist) > 0),
        before_after_pairs=before_after_pairs,
        before_im=before_im,
        after_im=after_im,
        has_2nd_im=has_2nd_im,
        before_2nd_im=before_2nd_im,
        after_2nd_im=after_2nd_im,
        has_extra_im=has_extra_im,
        extra1_im=extra1_im,
        extra2_im=extra2_im,
        questname=questname,
        dropdata=json.dumps(dropdata),
        contains_unknown_items=contains_unknown_items,
        image_url=image_url,
    )


def nparray_to_imagebytes(im):
    h, _ = im.shape[:2]
    # 解像度の高いものは半分にリサイズ
    if h >= 1000:
        resized_im = cv2.resize(im, dsize=None, fx=0.5, fy=0.5)
    else:
        resized_im = im
    ok, encoded_im = cv2.imencode('.jpg', resized_im)
    if ok:
        return base64.b64encode(encoded_im.tobytes())
    else:
        return None


def make_before_after_pairs(before_list, after_list, owned_diff):
    pairs = []
    for i, (before, after) in enumerate(zip(before_list, after_list)):
        logger.debug('[%s] before: %s, after: %s', i, before, after)
        before_id = before['id']
        after_id = after['id']

        if before_id == img2str.ID_NO_POSESSION or after_id == img2str.ID_NO_POSESSION:
            logger.debug('[%s]: skipping due to no posession (before: %s, after: %s)', i, before, after)
            continue

        before_dn = before['dropnum']
        after_dn = after['dropnum']

        if not str(before_dn).isdigit() or not str(after_dn).isdigit():
            logger.debug('[%s]: both or either dropnum is not digit (before: %s, after: %s)', i, before, after)
            continue

        if before_id != after_id:
            if not (before_id == img2str.ID_UNDROPPED and after_id != img2str.ID_UNDROPPED):
                continue

            owned_items = [e for e in owned_diff if e['id'] == after_id]
            # 周回前画像が未ドロップ、かつ補完情報が見つからない
            if not owned_items:
                logger.debug('[%s]: owned item not found. skip (before: %s, after: %s)', i, before, after)
                continue
            owned_item = owned_items[0]
            logger.debug('owned item found: %s', owned_item)

            # ここで補完情報を用いて周回前情報を上書きする
            before_dn = owned_item['dropnum']

        pair = (after['name'], before_dn, after_dn, after_dn - before_dn)
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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='localhost', help='listen host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='listen port (default: 8080)')
    parser.add_argument('--loglevel', choices=('debug', 'info'), default='info')
    return parser.parse_args()


if __name__ == "__main__":
    # appengine 上では / アクセスのときは static な index.html
    # を返すので handler は不要だが、ローカルで動かす場合は必要。
    import os
    from bottle import static_file

    static_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    @app.get('/')
    def index():
        return static_file('index.html', root=static_root)

    @app.route('/static/<filepath:path>')
    def static_content(filepath):
        return static_file(filepath, root=static_root)

    args = parse_args()
    logger.setLevel(args.loglevel.upper())
    logger.info('loglevel: %s', args.loglevel)
    app.run(host=args.host, port=args.port)
