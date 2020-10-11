#!/usr/bin/env python3
import argparse
import base64
import copy
import io
import itertools
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
        logger.warning('file is None')
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


class CannotAnalyzeError(Exception):
    pass


class ScreenShotBundle:
    def __init__(self, before_files, after_files, owned_files):
        if len(before_files) != len(after_files):
            msg = 'the number of before_files ({}) must be equal to the number of after_files ({})'
            raise ValueError(msg.format(len(before_files), len(after_files)))

        self.svm = cv2.ml.SVM_load(str(img2str.training))
        self.dropitems = img2str.DropItems(storage=storage)
        self.before_files = before_files
        self.after_files = after_files
        self.owned_files = owned_files
        # これらは analyze() の後に値が設定される
        self.before_images = []
        self.after_images = []
        self.owned_images = []
        self.before_sc_objects = []
        self.after_sc_objects = []
        self.owned_diff = []
        self.before_sc = None
        self.after_sc = None
        self.parse_result = None

    def analyze(self):
        self.after_sc, self.after_sc_itemlist = self._analyze_after_files()
        self.before_sc, self.before_sc_itemlist = self._analyze_before_files()

        logger.info('sc before: %s', self.before_sc_itemlist)
        logger.info('sc after: %s', self.after_sc_itemlist)

        missing_items = dropitemseditor.detect_missing_item(self.after_sc_itemlist, self.before_sc_itemlist)
        logger.info('missing items: %s', missing_items)

        if self.owned_files:
            _, owned_list = dropitemseditor.read_owned_ss(self.owned_files, self.dropitems, self.svm, missing_items)
            logger.info('owned list: %s', owned_list)
            self.owned_diff = dropitemseditor.make_owned_diff(self.before_sc_itemlist, self.after_sc_itemlist, owned_list)
            logger.info('owned diff: %s', self.owned_diff)

        for of in self.owned_files:
            # dropitemseditor.read_owned_ss() で終端まで読み取り済みなので
            # seek 位置を先頭に戻してやらないと imdecode できない。
            of.seek(0)
            na = cv2.imdecode(get_np_array(of), 1)
            im = nparray_to_imagebytes(na)
            self.owned_images.append(im)

        self.parse_result = dropitemseditor.make_diff(
            copy.deepcopy(self.before_sc_itemlist),
            copy.deepcopy(self.after_sc_itemlist),
            owned=self.owned_diff,
        )
        logger.info('parse_result: %s', self.parse_result)

    def _analyze_before_files(self):
        """ 先に _analyze_after_files() を呼び出しておくこと
        """
        for i, f in enumerate(self.before_files):
            im = cv2.imdecode(get_np_array(f.file), 1)
            self.before_images.append(im)
            sc = img2str.ScreenShotBefore(im, self.svm, self.dropitems, self.after_sc_objects[i].itemlist)
            if len(sc.itemlist) == 0:
                logger.warning('cannot recognize image')
                if sc.error:
                    logger.warning('error: %s', sc.error)
                message=(
                    '周回後画像が認識できません。'
                    f'アップロードしたファイル {f.filename} に間違いがないか確認してください。'
                )
                raise CannotAnalyzeError(message)
            self.before_sc_objects.append(sc)
        return dropitemseditor.detect_upper(self.before_sc_objects), dropitemseditor.merge_sc(self.before_sc_objects)

    def _analyze_after_files(self):
        for f in self.after_files:
            im = cv2.imdecode(get_np_array(f.file), 1)
            self.after_images.append(im)
            sc = img2str.ScreenShot(im, self.svm, self.dropitems)
            if len(sc.itemlist) == 0:
                logger.warning('cannot recognize image')
                if sc.error:
                    logger.warning('error: %s', sc.error)
                message=(
                    '周回後画像が認識できません。'
                    f'アップロードしたファイル {f.filename} に間違いがないか確認してください。'
                )
                raise CannotAnalyzeError(message)
            self.after_sc_objects.append(sc)
        return dropitemseditor.detect_upper(self.after_sc_objects), dropitemseditor.merge_sc(self.after_sc_objects)

    def image_pairs(self):
        return itertools.zip_longest(self.before_images, self.after_images)

    def encoded_image_pairs(self):
        return [
            (nparray_to_imagebytes(before), nparray_to_imagebytes(after))
            for before, after in itertools.zip_longest(self.before_images, self.after_images)
        ]


@app.post('/upload')
def upload_post():
    before_files = request.files.getall('before')
    after_files = request.files.getall('after')
    extra_files = request.files.getall('extra')

    logger.info('test before_files')
    if len(before_files) == 0:
        logger.warning('before_files is blank')
        redirect('/')
    for i, f in enumerate(before_files):
        logger.info('test before_file %s', i)
        if not is_valid_file(f):
            redirect('/')

    logger.info('test after_files')
    if len(after_files) == 0:
        logger.warning('after_files is blank')
        redirect('/')
    for i, f in enumerate(after_files):
        logger.info('test after_file %s', i)
        if not is_valid_file(f):
            redirect('/')

    owned_files = []
    logger.info('test extra_files')
    for i, f in enumerate(extra_files):
        logger.info('test extra_file %s', i)
        if is_valid_file(f):
            logger.info('extra_file %s found', i)
            owned_files.append(f.file)
        else:
            logger.info('extra_file %s not found')

    bundle = ScreenShotBundle(before_files, after_files, owned_files)
    try:
        bundle.analyze()
    except CannotAnalyzeError as e:
        logger.error(e)
        return template('error', message=str(e))

    questname, questdrop = dropitemseditor.get_questinfo(bundle.before_sc, bundle.after_sc)
    logger.info('quest: %s', questname)
    logger.info('questdrop: %s', questdrop)

    drops_diff = dropitemseditor.DropsDiff(bundle.parse_result, questname, questdrop)
    parsed_obj = drops_diff.parse(bundle.dropitems)

    dropdata = parsed_obj.as_json_data()
    logger.info('dropdata json: %s', dropdata)

    # さらに web 向けに加工する
    for d in dropdata:
        d['order'] = d['id']
        d['initial'] = d['report']
        d['add'] = 0
        d['reduce'] = 0

    before_after_pairs = make_before_after_pairs(bundle.before_sc.itemlist, bundle.after_sc.itemlist, bundle.owned_diff)
    logger.info('pairs: %s', before_after_pairs)
    contains_unknown_items = any([pair[0].startswith('item0') for pair in before_after_pairs])

    return template('result',
        result=makeup(bundle.parse_result),
        sc1_available=(len(bundle.before_sc.itemlist) > 0),
        sc2_available=(len(bundle.after_sc.itemlist) > 0),
        before_after_pairs=before_after_pairs,
        image_pairs=bundle.encoded_image_pairs(),
        extra_images=bundle.owned_images,
        questname=questname,
        dropdata=json.dumps(dropdata),
        contains_unknown_items=contains_unknown_items,
    )


def nparray_to_jpeg(im):
    ok, encoded = cv2.imencode('.jpg', im)
    if ok:
        return encoded


def jpeg_to_imagebytes(encoded_im):
    return base64.b64encode(encoded_im.tobytes())


def nparray_to_imagebytes(im):
    jpg = nparray_to_jpeg(im)
    if jpg is not None:
        return jpeg_to_imagebytes(jpg)


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
