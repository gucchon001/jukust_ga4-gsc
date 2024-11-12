# config.py
import configparser
import os

def load_config():
    """設定ファイルを読み込む"""
    config = configparser.ConfigParser()
    config.read('settings.ini', encoding='utf-8')
    return config