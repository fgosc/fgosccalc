from logging import getLogger
from unittest import TestCase

from . import questdb

logger = getLogger(__name__)


class QuestTest(TestCase):
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
        ds = questdb.FreequestDataset()
        candidates = ds.guess_quests(items)

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
        ds = questdb.FreequestDataset()
        candidates = ds.guess_quests(items)

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
