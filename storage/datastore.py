import pickle
from logging import getLogger
from typing import Dict

import cv2  # type: ignore
import numpy as np  # type: ignore
from google.cloud import datastore  # type: ignore

logger = getLogger(__name__)
logger.setLevel('DEBUG')


class GoogleDatastoreStorage:
    def __init__(self, kind):
        self.client = datastore.Client()
        self.kind = kind

    def known_item_dict(self) -> Dict[str, np.ndarray]:
        query = self.client.query(kind=self.kind)
        items = list(query.fetch())
        logger.debug('known_item_dict> fetched %s items', len(items))
        return {item['name']: pickle.loads(item['image']) for item in items}

    def create_item(self, im: np.ndarray) -> str:
        query = self.client.query(kind=self.kind)
        query.order = ['-number']
        items = list(query.fetch(limit=1))
        if len(items) == 0:
            number = 0
        else:
            number = items[0]['number']
        number += 1
        logger.debug('create item> new number: %s', number)
        item_key = self.client.key(self.kind, number)
        item = datastore.Entity(key=item_key)
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        serialized = pickle.dumps(im_gray)
        item['number'] = number
        item['image'] = serialized
        name = 'item{:0=6}'.format(number)
        item['name'] = name
        item.exclude_from_indexes = ['image']
        self.client.put(item)
        return name
