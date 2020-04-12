import shutil
import tempfile
import unittest
from pathlib import Path

import cv2  # type: ignore
import numpy as np  # type: ignore

from .filesystem import FileSystemStorage


class FileSystemStorageTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.itemdir = Path(str(self.tempdir))

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_known_item_dict(self):
        st = FileSystemStorage(self.itemdir)
        im1 = self.make_random_cv2_image()
        ret1 = st.create_item(im1)
        im2 = self.make_random_cv2_image()
        ret2 = st.create_item(im2)

        (self.itemdir / 'item000001.png').replace(self.itemdir / 'test1.png')
        (self.itemdir / 'item000002.png').replace(self.itemdir / 'test2.png')

        d = st.known_item_dict()
        self.assertEqual(len(d), 2)
        for v in d.values():
            self.assertTrue(isinstance(v, np.ndarray))

    def test_create_item(self):
        st = FileSystemStorage(self.itemdir)
        im1 = self.make_random_cv2_image()
        ret1 = st.create_item(im1)
        self.assertEqual(ret1, 'item000001')
        im2 = self.make_random_cv2_image()
        ret2 = st.create_item(im2)
        self.assertEqual(ret2, 'item000002')
        im3 = self.make_random_cv2_image()
        ret3 = st.create_item(im3)
        self.assertEqual(ret3, 'item000003')

    def make_random_cv2_image(self):
        return np.random.randint(255, size=(128, 128, 3), dtype=np.uint8)
