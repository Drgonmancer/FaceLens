# -*- coding: utf-8 -*-
"""
FaceGuard 人脸识别系统 - 数据库配置向导
功能：交互式引导用户配置数据库连接信息
"""

import os
import sys
import getpass

def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════╗
║     FaceGuard 数据库配置向导                      ║
║     请按照提示输入您的 MySQL 数据库连接信息        ║
╚══════════════════════════════════════════════════╝
    """
    print(banner)

def get_input(prompt, default=None, required=True):
    """获取用户输入"""
    while True:
        if default:
            value = input(f"  {prompt} [默认: {default}]: ").strip()
            if not value:
                value = default
        else:
            value = input(f"  {prompt}: ").strip()
        
        if not value and required:
            print("  ⚠ 此项为必填项，请重新输入！")
            continue
        
        return value

def test_connection(host, port, user, password, db_name):
    """测试数据库连接"""
    try:
        import pymysql
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db_name,
            charset='utf8mb4',
            connect_timeout=5
        )
        conn.close()
        return True, "连接成功！"
    except ImportError:
        return True, "pymysql未安装，跳过连接测试（安装后会自动测试）"
    except Exception as e:
        return False, str(e)

def create_config_file(config_path, config_data):
    """创建配置文件"""
    content = f"""[sql]
;support two sql,mysql and mssql,choice one
type = mysql
host = {config_data['host']}
port = {config_data['port']}
user = {config_data['user']}
passwd = {config_data['password']}
db = {config_data['db_name']}
charset = utf8
"""
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ 配置文件已保存至: {config_path}")
    return True

def main():
    """主函数"""
    print_banner()
    
    # 获取脚本所在目录的上级目录（server_code目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.ini')
    
    print("\n📋 请输入 MySQL 数据库连接信息：\n")
    
    # 收集配置信息
    config = {}
    
    # 主机地址
    config['host'] = get_input("MySQL主机地址", "127.0.0.1")
    
    # 端口
    config['port'] = get_input("MySQL端口", "3306")
    
    # 用户名
    config['user'] = get_input("MySQL用户名", "root")
    
    # 密码（隐藏输入）
    print("\n  MySQL密码: ", end='')
    config['password'] = getpass.getpass('')
    if not config['password']:
        config['password'] = get_input("MySQL密码 (明文显示)", "", required=False)
        if not config['password']:
            config['password'] = ""
    
    # 数据库名
    config['db_name'] = get_input("数据库名称", "cl3286667")
    
    # 显示配置摘要
    print("\n" + "="*50)
    print("  配置信息确认：")
    print("="*50)
    print(f"  主机地址: {config['host']}")
    print(f"  端口号:   {config['port']}")
    print(f"  用户名:   {config['user']}")
    print(f"  密码:     {'*' * len(config['password']) if config['password'] else '(空)'}")
    print(f"  数据库:   {config['db_name']}")
    print("="*50)
    
    # 确认保存
    confirm = input("\n  确认保存配置? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("\n✗ 配置已取消！")
        return False
    
    # 测试连接
    print("\n  正在测试数据库连接...")
    success, message = test_connection(
        config['host'],
        config['port'],
        config['user'],
        config['password'],
        config['db_name']
    )
    
    if success:
        print(f"  ✓ {message}")
    else:
        print(f"  ⚠ 连接测试失败: {message}")
        print("  提示: 配置仍会保存，请确保后续启动时数据库可用")
    
    # 保存配置文件
    create_config_file(config_path, config)
    
    print("\n✓ 数据库配置完成！\n")
    return True

if __name__ == '__main__':
    try:
        result = main()
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n✗ 用户取消操作！")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        sys.exit(1)
