# -*- coding: utf-8 -*-
"""清除所有人脸样本、登录抓拍及数据库中的人脸相关记录。"""
import os
import shutil
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
os.chdir(BASE)

def clean_files():
    for sub in ('face_train', 'login_faces'):
        d = os.path.join(BASE, 'templates', 'file', sub)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if name == '.gitkeep':
                continue
            path = os.path.join(d, name)
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        print(f'[OK] 已清空 {sub}/')

def clean_database():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj2.settings')
    import django
    django.setup()
    from django.db import connection
    from main.models import loginrecord, faceregister, yonghu, syslog

    n1 = loginrecord.objects.count()
    loginrecord.objects.all().delete()
    print(f'[OK] loginrecord 删除 {n1} 条')

    n2 = faceregister.objects.count()
    faceregister.objects.all().delete()
    print(f'[OK] faceregister 删除 {n2} 条')

    updated = yonghu.objects.update(
        faceregistered=0, facecount=0, touxiang=''
    )
    print(f'[OK] yonghu 已重置人脸字段（{updated} 条）')

    # 操作日志中可能含 base64 人脸参数
    n3 = syslog.objects.filter(params__icontains='face').count()
    syslog.objects.filter(params__icontains='face').delete()
    print(f'[OK] syslog 含 face 参数删除 {n3} 条')

    with connection.cursor() as cur:
        cur.execute("DELETE FROM loginrecord")
        cur.execute("DELETE FROM faceregister")
        cur.execute(
            "UPDATE yonghu SET faceregistered=0, facecount=0, touxiang=''"
        )
    print('[OK] SQL 二次确认完成')

if __name__ == '__main__':
    print('=== FaceGuard 隐私数据清理 ===\n')
    clean_files()
    try:
        clean_database()
    except Exception as e:
        print(f'[WARN] 数据库清理失败（请确认 MySQL 已启动且 config.ini 正确）: {e}')
        sys.exit(1)
    print('\n=== 清理完成 ===')
