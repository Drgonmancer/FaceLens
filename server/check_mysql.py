# -*- coding: utf-8 -*-
"""测试 MySQL 连接（读取 config.ini，无硬编码密码）。"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

from util.configread import config_read

ini = os.path.join(BASE, 'config.ini')
if not os.path.isfile(ini):
    print('请先创建 config.ini（可复制 config.ini.example）')
    sys.exit(1)

dbtype, host, port, user, passwd, db, charset = config_read(ini)
import pymysql
conn = pymysql.connect(host=host, port=port, user=user, password=passwd, database=db, charset='utf8mb4')
conn.close()
print('MySQL 连接成功')
