from pathlib import Path
from typing import Dict

import cv2  # type: ignore
import numpy as np  # type:ignore

from . import CannotCreateItemError


class FileSystemStorage:
    """
        ファイルシステムを用いた Storage
    """
    def __init__(self, itemdir: Path):
        # TODO: itemdir.mkdir(exist_ok=True) だと GAE でエラーになる。
        # GAE は readonly filesystem であるため。少なくとも GAE 向けの
        # 実装を FileSystemStorage 非依存にするまではこの実装でないと
        # まずい。
        if not itemdir.exists():
            itemdir.mkdir(parents=True)
        self.itemdir = itemdir

    def known_item_dict(self) -> Dict[str, np.ndarray]:
        items = {}
        files = self.itemdir.glob('**/*.png')
        for f in files:
            im = self._imread(str(f))
            if im is not None:
                items[f.stem] = im
        return items

    def _imread(self,
                filename: str,
                flags: int = cv2.IMREAD_COLOR,
                dtype: float = np.uint8) -> np.ndarray:
        n = np.fromfile(filename, dtype)
        return cv2.imdecode(n, flags)

    def create_item(self, im: np.ndarray) -> str:
        for i in range(1, 100000):
            itemfile = self.itemdir / ('item{:0=6}'.format(i) + '.png')
            if itemfile.is_file():
                continue

            im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(itemfile.as_posix(), im_gray)
            return itemfile.stem

        raise CannotCreateItemError('unable to allocate a resource')
