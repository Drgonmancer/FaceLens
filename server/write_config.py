# -*- coding: utf-8 -*-
"""启动时输入 MySQL 密码，验证连接后写入 config.ini。"""
import getpass
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE, 'config.ini')

host = os.environ.get('FG_DB_HOST', '127.0.0.1')
port = int(os.environ.get('FG_DB_PORT', '3306'))
user = os.environ.get('FG_DB_USER', 'root')
db = os.environ.get('FG_DB_NAME', 'cl3286667')


def ask_password():
    print()
    print('========================================')
    print('  MySQL 数据库连接')
    print('========================================')
    print(f'  主机: {host}')
    print(f'  端口: {port}')
    print(f'  用户: {user}')
    print(f'  数据库: {db}')
    print('----------------------------------------')
    while True:
        passwd = getpass.getpass('  请输入 MySQL 密码: ')
        if passwd:
            return passwd
        print('  [提示] 密码不能为空，请重新输入。')


def test_connection(passwd):
    import pymysql

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=passwd,
        charset='utf8mb4',
        connect_timeout=5,
    )
    conn.close()


def write_config(passwd):
    content = f"""[sql]
type = mysql
host = {host}
port = {port}
user = {user}
passwd = {passwd}
db = {db}
charset = utf8
"""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    passwd = os.environ.get('FG_DB_PASS', '').strip()
    if not passwd:
        passwd = ask_password()

    print()
    print('[INFO] 正在验证数据库连接...')
    try:
        test_connection(passwd)
    except Exception as exc:
        print(f'[ERROR] 数据库连接失败: {exc}')
        print('[提示] 请确认 MySQL 已启动且密码正确，然后重新运行 start.bat')
        return 1

    write_config(passwd)
    print('[OK] 数据库连接成功，配置已保存')
    return 0


if __name__ == '__main__':
    sys.exit(main())
