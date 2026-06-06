# -*- coding: utf-8 -*-
"""启动前检查：config.ini、MySQL 连接、数据库与表结构。"""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
os.chdir(BASE)

from util.configread import config_read

CONFIG_PATH = os.path.join(BASE, 'config.ini')
SQL_PATH = os.path.join(BASE, 'sql', 'cl3286667.sql')
PLACEHOLDER = 'YOUR_MYSQL_PASSWORD_HERE'


def fail(msg, code=1):
    print(f'[错误] {msg}')
    sys.exit(code)


def ensure_config():
    if not os.path.isfile(CONFIG_PATH):
        fail('缺少 server/config.ini，请通过 start.bat 启动以自动生成')

    dbtype, host, port, user, passwd, db_name, charset = config_read(CONFIG_PATH)
    if not dbtype or not db_name:
        fail('config.ini 格式不正确，请运行: python setup_config.py')
    if passwd == PLACEHOLDER or passwd is None:
        fail('数据库密码未配置，请检查 start.bat 中的 FG_DB_PASS')
    return dbtype, host, port, user, passwd, db_name.replace(' ', '').strip(), charset


def import_sql(host, port, user, passwd, db_name):
    import subprocess

    mysql_bin = 'mysql'
    for candidate in (
        r'D:\code\MySQL\mysql-8.4.8-winx64\bin\mysql.exe',
        r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe',
        r'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe',
    ):
        if os.path.isfile(candidate):
            mysql_bin = candidate
            break

    env = os.environ.copy()
    if passwd:
        env['MYSQL_PWD'] = passwd

    cmd = [
        mysql_bin,
        '-h', str(host),
        '-P', str(port),
        '-u', user,
        db_name,
    ]
    with open(SQL_PATH, encoding='utf-8') as sql_file:
        result = subprocess.run(
            cmd,
            stdin=sql_file,
            capture_output=True,
            text=True,
            env=env,
        )
    if result.returncode != 0:
        fail(f'导入 SQL 失败：{result.stderr.strip() or result.stdout.strip()}')


def ensure_database(dbtype, host, port, user, passwd, db_name, charset='utf8mb4'):
    import pymysql

    if dbtype != 'mysql':
        fail('当前仅支持 MySQL，请检查 config.ini 中 type = mysql')

    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=passwd,
            charset='utf8mb4', connect_timeout=5
        )
    except Exception as exc:
        fail(f'无法连接 MySQL ({host}:{port})：{exc}')

    with conn.cursor() as cur:
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cur.execute(f"USE `{db_name}`")
        cur.execute("SHOW TABLES LIKE 'yonghu'")
        has_core_table = cur.fetchone() is not None

    if not has_core_table:
        if not os.path.isfile(SQL_PATH):
            conn.close()
            fail(f'缺少初始化脚本: {SQL_PATH}')
        print('[提示] 正在初始化数据库表结构...')
        conn.close()
        import_sql(host, port, user, passwd, db_name)
        print('[成功] 数据库初始化完成')
        print('[成功] MySQL 连接正常，数据库已就绪')
        return

    conn.close()
    print('[成功] MySQL 连接正常，数据库已就绪')


def main():
    cfg = ensure_config()
    ensure_database(*cfg)
    print('[就绪] 可以启动服务')


if __name__ == '__main__':
    main()
