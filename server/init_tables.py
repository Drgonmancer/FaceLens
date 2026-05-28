# -*- coding: utf-8 -*-
"""初始化 systemconfig 等表数据（需 config.ini）。"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

from util.configread import config_read
import pymysql

ini = os.path.join(BASE, 'config.ini')
if not os.path.isfile(ini):
    print('请先创建 config.ini')
    sys.exit(1)

_, host, port, user, passwd, db, _ = config_read(ini)
conn = pymysql.connect(
    host=host, port=port, user=user, password=passwd,
    database=db.replace(' ', '').strip(), charset='utf8mb4'
)
cur = conn.cursor()
cur.execute(
    "INSERT IGNORE INTO systemconfig (configkey, configvalue, description) "
    "VALUES ('face_threshold', '70', '人脸识别匹配阈值')"
)
conn.commit()
conn.close()
print('init_tables 完成')
