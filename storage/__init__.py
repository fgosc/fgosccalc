from typing import Dict

import numpy as np  # type: ignore


class CannotCreateItemError(Exception):
    """
        アイテムを新規に作ることができないことを示す例外
    """
    pass


class Storage:
    """
        抽象化されたストレージ層。
        具体的な実装は、このクラスで定義されたメソッドを実装して
        いることが義務付けられる。

        利用者がこのクラスを直接用いることはできない。
        あくまでストレージ層が守るべき契約を定めたものである。
    """
    def known_item_dict(self) -> Dict[str, np.ndarray]:
        """
            既知のアイテムを辞書形式で返す。
            {アイテム名: im (OpenCV の画像オブジェクト), ...}
        """
        raise NotImplementedError

    def create_item(self, im: np.ndarray) -> str:
        """
            im (OpenCV の画像オブジェクト) を受け取って永続化し、
            新たに割り当てられたアイテム名を返す。
        """
        raise NotImplementedError
