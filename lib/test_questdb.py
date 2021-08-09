from logging import getLogger
from unittest import TestCase

from . import questdb
from .consts import ID_UNDROPPED, ID_NO_POSESSION

logger = getLogger(__name__)


class QuestTest(TestCase):
    def setUp(self):
        self.fqDataset = questdb.FreequestDataset()

    def test_build_questdb(self):
        quests = questdb.build_questdb()
        self.assertTrue(len(quests) > 0)
        q0 = quests[0]
        self.assertIn("id", q0)
        self.assertIn("name", q0)
        self.assertIn("place", q0)
        self.assertIn("chapter", q0)
        self.assertIn("qp", q0)
        self.assertIn("drop", q0)
        self.assertIn("dropSelected", q0)
        self.assertIn("shortname", q0)
        self.assertEqual(len(q0.keys()), 8)

        drops = q0["drop"]
        self.assertTrue(len(drops) > 0)
        drop0 = drops[0]

        self.assertIn("id", drop0)
        self.assertIn("name", drop0)
        self.assertIn("type", drop0)
        self.assertIn("dropPriority", drop0)
        self.assertEqual(len(drop0.keys()), 4)

    def test_guess_quests__single_place(self):
        items = [
            {"id": 6515}, # 八連双晶
            {"id": 6505}, # 虚影の塵
            {"id": 6503}, # 英雄の証
            {"id": 6001}, # 剣の輝石
            {"id": 6002}, # 弓の輝石
            {"id": 6007}, # 狂の輝石
            {"id": 7007}, # バーサーカーピース
        ]
        candidates = self.fqDataset.guess_quests(items)

        self.assertEqual(len(candidates), 1)

        c: questdb.QuestDict = candidates[0]
        self.assertEqual(c["chapter"], "セプテム")
        self.assertEqual(c["place"], "連合首都")
        self.assertEqual(c["name"], "ローマの地平")

    def test_guess_quests__multiple_places(self):
        items = [
            {"id": 6512}, # 竜の牙
            {"id": 6104}, # 騎の魔石
            {"id": 6004}, # 騎の輝石
        ]
        candidates = self.fqDataset.guess_quests(items)

        self.assertEqual(len(candidates), 3)

        c0: questdb.QuestDict = candidates[0]
        self.assertEqual(c0["chapter"], "バビロニア")
        self.assertEqual(c0["place"], "エリドゥ")
        self.assertEqual(c0["name"], "王権の地")

        c1: questdb.QuestDict = candidates[1]
        self.assertEqual(c1["chapter"], "北米")
        self.assertEqual(c1["place"], "デミング")
        self.assertEqual(c1["name"], "ニューシカゴ")

        c2: questdb.QuestDict = candidates[2]
        self.assertEqual(c2["chapter"], "オケアノス")
        self.assertEqual(c2["place"], "翼竜の島")
        self.assertEqual(c2["name"], "竜たちの楽園")

    def test_guess_quests__has_undropped_01(self):
        # 種火のドロップが欠けているケース 01
        items = [
            {"id": 6526}, # 追憶の貝殻
            {"id": 6534}, # 励振火薬
            {"id": 6001}, # 剣の輝石
            {"id": 6007}, # 狂の輝石
            {"id": ID_NO_POSESSION}, # 種火1
            {"id": ID_UNDROPPED},    # 種火2 未ドロップ
            {"id": ID_NO_POSESSION}, # 種火3
        ]
        candidates = self.fqDataset.guess_quests(items)

        self.assertEqual(len(candidates), 1)

        c0: questdb.QuestDict = candidates[0]
        self.assertEqual(c0["chapter"], "アナスタシア")
        self.assertEqual(c0["place"], "焼き払われた村")
        self.assertEqual(c0["name"], "雪に沈む焼け跡")

    def test_guess_quests__has_undropped_02(self):
        # 種火のドロップが欠けているケース 02
        items = [
            {"id": 6516}, # 凶骨
            {"id": 6001}, # 剣の輝石
            {"id": ID_UNDROPPED},    # 未ドロップ
            {"id": ID_UNDROPPED},    # 未ドロップ
            {"id": ID_UNDROPPED},    # 未ドロップ
            {"id": ID_NO_POSESSION}, # QP
        ]
        candidates = self.fqDataset.guess_quests(items)

        # TODO 一致しすぎているので、何らかの手段を加えることで絞り込みを強化したい。
        self.assertEqual(len(candidates), 4)

        c0: questdb.QuestDict = candidates[0]
        self.assertEqual(c0["chapter"], "冬木")
        self.assertEqual(c0["place"], "未確認座標X-A")
        self.assertEqual(c0["name"], "屋敷跡")

        c1: questdb.QuestDict = candidates[1]
        self.assertEqual(c1["chapter"], "冬木")
        self.assertEqual(c1["place"], "未確認座標X-D")
        self.assertEqual(c1["name"], "紅く染まった港")

        c2: questdb.QuestDict = candidates[2]
        self.assertEqual(c2["chapter"], "冬木")
        self.assertEqual(c2["place"], "未確認座標X-C")
        self.assertEqual(c2["name"], "大橋")

        c3: questdb.QuestDict = candidates[3]
        self.assertEqual(c3["chapter"], "冬木")
        self.assertEqual(c3["place"], "未確認座標X-B")
        self.assertEqual(c3["name"], "爆心地")
