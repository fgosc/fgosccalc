import json
from pathlib import Path
from typing import Any, Dict, List, Optional

ItemDict = Dict[str, Any]
QuestDict = Dict[str, Any]

# TODO consts.py とか作ってそこにまとめる
ID_UNDROPPED: int = -2
ID_NO_POSESSION: int = -1

DATADIR_BASE: Path = Path(__file__).resolve().parent.parent


def build_questdb() -> List[QuestDict]:
    quest_dir = DATADIR_BASE / Path("fgoscdata/data/json/")

    questfiles = quest_dir.glob('**/*.json')
    all_quests = []
    for questfile in questfiles:
        with open(questfile, encoding='UTF-8') as f:
            quests = json.load(f)
            all_quests.extend(quests)

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

    def guess_quests(self, items: List[ItemDict]) -> List[QuestDict]:
        """
        アイテムリストからクエスト名の候補（複数）を推測して、対応する QuestDict のリストを返す。
        アイテムリストには以下の構造を要求する:
        
        [
            {"id": 1234},
            {"id": 1235},
            ...
        ]
        """
        # 未ドロップは除外
        cleaned_items = [item for item in items if item["id"] != ID_NO_POSESSION]
        candidates = []

        for quest in self.freequests:
            if self._match_drops(cleaned_items, quest["dropSelected"]):
                # if self.droplist == []:
                #    # 最初に見つかったdroplistを使用
                #    self.droplist = [item["name"] for item in quest["drop"]]
                candidates.append(quest)

        return candidates

    def _match_drops(self, scitems: List[ItemDict], fqitems: List[ItemDict]) -> bool:
        """
        フリクエのドロップアイテムと画像のドロップアイテムを比較
        """
        if len(fqitems) > 12:
            fqitems = fqitems[:12]

        if len(scitems) != len(fqitems):
            return False

        for sc, fq in zip(scitems, fqitems):
            if sc["id"] == ID_UNDROPPED:
                if self.item_dataset.is_craft_essence(fq["id"]):
                    continue
                else:
                    return False
            elif sc["id"] != fq["id"]:
                return False
        return True
