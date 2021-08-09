import json
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .consts import ID_UNDROPPED, ID_NO_POSESSION

ItemDict = Dict[str, Any]
QuestDict = Dict[str, Any]

DATADIR_BASE: Path = Path(__file__).resolve().parent.parent

logger = getLogger(__name__)


def build_questdb() -> List[QuestDict]:
    quest_dir = DATADIR_BASE / Path("fgoscdata/data/json/")

    questfiles = quest_dir.glob('**/*.json')
    all_quests = []
    for questfile in questfiles:
        with open(questfile, encoding='UTF-8') as f:
            quests = json.load(f)
            all_quests.extend(quests)

    # 比較用にポイント、種火、QPを除いたドロップリストを用意しておく
    # TODO 改良版で不要になるかも
    for quest in all_quests:
        quest["dropSelected"] = [
            drop for drop in quest["drop"]
            if drop["type"] not in ["Point", "Exp. UP"] or drop["name"] == "QP"
        ]

    return all_quests


def build_itemdb() -> List[ItemDict]:
    drop_file = DATADIR_BASE / Path("fgoscdata/hash_drop.json")

    with open(drop_file, encoding='UTF-8') as f:
        return json.load(f)


class Item:
    def __init__(self, item: ItemDict):
        self.item = item

    def is_undropped(self):
        return self.item["id"] == ID_UNDROPPED

    def is_no_possession(self):
        return self.item["id"] == ID_NO_POSESSION

    @property
    def item_id(self) -> int:
        return self.item["id"]


class DBItem:
    def __init__(self, item: ItemDict):
        self.item = item

    def countable(self):
        return self.item["type"] != "Exp. UP"

    def is_point(self):
        return self.item["type"] == "Point"

    def is_qp(self):
        return self.item["name"] == "QP"

    @property
    def item_id(self) -> int:
        return self.item["id"]


class ItemDataset:
    def __init__(self):
        self.items: List[ItemDict] = build_itemdb()
        self.item_index: Dict[int, ItemDict] = {}

        for item in self.items:
            self.item_index[item["id"]] = item

    def get_item(self, item_id: int) -> Optional[ItemDict]:
        return self.item_index.get(item_id)

    def get_item_type(self, item_id: int) -> Optional[str]:
        item = self.item_index.get(item_id)
        if not item:
            return None
        return item.get("type")

    def is_craft_essence(self, item_id: int) -> bool:
        item_type = self.get_item_type(item_id)
        return item_type == "Craft Essence"


class FreequestDataset:
    def __init__(self):
        self.item_dataset = ItemDataset()
        self.freequests = build_questdb()
        # reverse するのは 未確認座標X-Cを未確認座標X-Bより先に認識させるため
        # TODO priority をつければよいのでは？
        self.freequests.reverse()

    def guess_quests(self, items: List[ItemDict], with_ratio=False) -> List[QuestDict]:
        """
        アイテムリストからクエスト名の候補（複数）を推測して、対応する QuestDict のリストを返す。
        アイテムリストには以下の構造を要求する:
        
        [
            {"id": 1234},
            {"id": 1235},
            ...
        ]
        """
        candidates: List[Tuple[ItemDict, float]] = []

        for quest in self.freequests:
            match_ratio = self._match_drops(items, quest["drop"])

            # 少なくともクエスト戦利品一覧 (種火など比較不可能なものは除外) の 2/3 以上の
            # アイテムと一致すること。一致数が少なければ少ないほど候補を絞り切れなくなるので、
            # ある程度の一致数は求めていく必要がある。
            if match_ratio > 0.6666:
                candidates.append((quest, match_ratio))

        # 一致率の高いほうが上に来るようにする
        candidates.sort(key=lambda x: x[1], reverse=True)

        # TODO このロジックを入れる場合、戦利品枠数の情報もないと厳しい。
        # 未ドロップが多いときに、絞り込みすぎてしまうリスクがある。
        # 未ドロップも含めた枠数を戦利品枠数と比較するようなチェックを入れられれば、これを回避できそうな気がする。

        # # 一致率 1.0 のものがある場合、他は捨てて良い
        # completely_match_quests_with_ratio = [c for c in candidates if c[1] == 1.0]
        # if completely_match_quests_with_ratio:
        #     if with_ratio:
        #         return completely_match_quests_with_ratio
        #     return [c[0] for c in candidates]

        if with_ratio:
            return candidates
        return [c[0] for c in candidates]

    def _match_drops(self, scitems: List[ItemDict], fqitems: List[ItemDict]) -> float:
        """
        フリクエのドロップアイテムと画像のドロップアイテムを比較する。
        一致率 (0 から 1) を返す。一致しないと判断された場合は 0 を返す。
        """
        if len(fqitems) > 12:
            fqitems = fqitems[:12]

        sc_idx = fq_idx = 0
        compared_count = 0

        # 比較可能なアイテムの一覧
        fq_comparable_items = [item for item in fqitems if DBItem(item).countable()]

        while sc_idx < len(scitems) and fq_idx < len(fqitems):
            scitem = Item(scitems[sc_idx])
            fqitem = DBItem(fqitems[fq_idx])

            # 所持数なしアイテムは比較対象ではない。
            # fq は動かさずに sc のインデックスだけを先に進める。
            if scitem.is_no_possession():
                sc_idx += 1
                continue

            # 未ドロップは比較対象かもしれないし、
            # 実は所持数なしアイテムで比較不要かもしれない。
            if scitem.is_undropped():
                # NOTE 比較対象であると仮定し、両方のインデックスを先に進めている。
                # しかしこれだと、実は所持数なしアイテムだった場合に以降の比較で
                # fq のインデックスがずれて誤認が起きる可能性が残る。
                sc_idx += 1
                fq_idx += 1
                continue

            if scitem.item_id != fqitem.item_id:
                logger.debug("does not match: %s != %s", scitem, fqitem)
                return 0

            compared_count += 1
            sc_idx += 1
            fq_idx += 1

        return compared_count / len(fq_comparable_items)
