"""
    setting.ini を管理するモジュール
"""

import pathlib


def setting_file_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2] / 'setting.ini'
