#coding:utf-8
__author__ = "ila"
import os
import json
import base64
import time
import uuid
import random
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q
from .models import yonghu, loginrecord, faceregister, systemconfig
from .users_model import users
from util.codes import *
from util.auth import Auth

def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')

def _save_login_record(username, role, logintype, userid=None, score=None, ipaddr=None,
                       useragent=None, result='成功', faceimage=None, isstranger=0):
    try:
        record = loginrecord(
            username=username,
            role=role,
            logintype=logintype,
            userid=userid,
            score=score,
            ipaddress=ipaddr or '',
            useragent=useragent or '',
            result=result,
            faceimage=faceimage or '',
            isstranger=isstranger
        )
        record.save()
        return record.id
    except Exception as e:
        print(f'保存登录记录失败: {e}')
        return None

def _save_face_image(base64_str):
    try:
        if not base64_str:
            return None
        upload_dir = os.path.join(os.getcwd(), "templates", "file", "login_faces")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = f"login_{uuid.uuid4().hex[:12]}_{int(time.time())}.jpg"
        filepath = os.path.join(upload_dir, filename)
        if ',' in base64_str:
            b64data = base64_str.split(',')[1]
        else:
            b64data = base64_str
        img_data = base64.b64decode(b64data)
        with open(filepath, 'wb') as f:
            f.write(img_data)
        return f"/file/login_faces/{filename}"
    except Exception as e:
        print(f'保存人脸图片失败: {e}')
        return None

def face_login_record(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {}}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        get_data = request.GET.dict()
        req_dict.update(get_data)
        
        page = int(req_dict.get('page', 1))
        limit = int(req_dict.get('limit', 10))
        username_filter = req_dict.get('username', '')
        role_filter = req_dict.get('role', '')
        logintype_filter = req_dict.get('logintype', '')
        result_filter = req_dict.get('result', '')
        start_date = req_dict.get('startDate', '')
        end_date = req_dict.get('endDate', '')
        q = Q()
        if username_filter:
            q &= Q(username__icontains=username_filter)
        if role_filter:
            q &= Q(role=role_filter)
        if logintype_filter:
            q &= Q(logintype=logintype_filter)
        if result_filter:
            q &= Q(result=result_filter)
        if start_date:
            q &= Q(addtime__gte=start_date)
        if end_date:
            q &= Q(addtime__lte=end_date + ' 23:59:59')
        total = loginrecord.objects.filter(q).count()
        offset = (page - 1) * limit
        records = loginrecord.objects.filter(q).order_by('-id')[offset:offset+limit]
        data_list = []
        for r in records:
            d = {
                'id': r.id,
                'addtime': r.addtime.strftime('%Y-%m-%d %H:%M:%S') if r.addtime else '',
                'username': r.username,
                'role': r.role,
                'logintype': r.logintype,
                'userid': r.userid,
                'score': r.score,
                'ipaddress': r.ipaddress,
                'useragent': (r.useragent[:80] + '..') if r.useragent and len(r.useragent) > 80 else (r.useragent or ''),
                'result': r.result,
                'faceimage': r.faceimage,
                'isstranger': r.isstranger,
            }
            data_list.append(d)
        msg['data'] = {
            'list': data_list,
            'currPage': page,
            'totalPage': (total + limit - 1) // limit,
            'total': total,
            'pageSize': limit
        }
        return JsonResponse(msg)

def face_login_stats(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {}}
        today = datetime.now().strftime('%Y-%m-%d')
        total = loginrecord.objects.count()
        today_count = loginrecord.objects.filter(addtime__gte=today).count()
        success_count = loginrecord.objects.filter(result='成功').count()
        fail_count = loginrecord.objects.filter(result='失败').count()
        face_count = loginrecord.objects.filter(logintype='人脸').count()
        pwd_count = loginrecord.objects.filter(logintype='密码').count()
        stranger_count = loginrecord.objects.filter(isstranger=1).count()
        admin_count = loginrecord.objects.filter(role='管理员').count()
        user_count = loginrecord.objects.filter(role='用户').count()
        visitor_count = loginrecord.objects.filter(role='游客').count()
        from django.db.models import Avg
        avg_score = loginrecord.objects.filter(score__isnull=False, result='成功').aggregate(avg=Avg('score'))['avg']
        msg['data'] = {
            'total': total,
            'todayCount': today_count,
            'successCount': success_count,
            'failCount': fail_count,
            'faceCount': face_count,
            'pwdCount': pwd_count,
            'strangerCount': stranger_count,
            'adminCount': admin_count,
            'userCount': user_count,
            'visitorCount': visitor_count,
            'avgScore': round(float(avg_score), 2) if avg_score else 0,
        }
        return JsonResponse(msg)

def face_register_api(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        userid = req_dict.get('userid')
        face_base64 = req_dict.get('face')
        action = req_dict.get('action', 'register')
        if not userid or not face_base64:
            msg['code'] = 400
            msg['msg'] = '缺少必要参数'
            return JsonResponse(msg)
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        if action == 'register':
            ok, result_msg = ocv.register_face_from_base64(int(userid), face_base64)
            if ok:
                quality, details = ocv.check_quality_from_base64(face_base64)
                is_admin = req_dict.get('_isAdmin', False)
                if is_admin:
                    user_obj = users.objects.filter(id=int(userid)).first()
                    username = user_obj.username if user_obj else str(userid)
                else:
                    user_obj = yonghu.objects.filter(id=int(userid)).first()
                    username = user_obj.yonghuzhanghao if user_obj else str(userid)
                face_path = _save_face_image(face_base64)
                fr = faceregister(
                    userid=int(userid),
                    username=username,
                    faceimage=face_path or '',
                    qualityscore=float(quality) if isinstance(quality, (int, float)) else 0,
                    isvalid=1
                )
                fr.save()
                face_count = ocv.get_face_count(int(userid))
                if is_admin:
                    pass
                else:
                    yonghu.objects.filter(id=int(userid)).update(faceregistered=1, facecount=face_count)
                msg['msg'] = result_msg
                msg['data'] = {'faceCount': face_count, 'quality': quality}
            else:
                msg['code'] = 400
                msg['msg'] = result_msg
        elif action == 'delete_all':
            ocv.delete_user_faces(int(userid))
            yonghu.objects.filter(id=int(userid)).update(faceregistered=0, facecount=0)
            faceregister.objects.filter(userid=int(userid)).update(isvalid=0)
            msg['msg'] = '已清除所有人脸数据'
        elif action == 'check':
            face_count = ocv.get_face_count(int(userid))
            registered = yonghu.objects.filter(id=int(userid)).values('faceregistered', 'facecount').first()
            msg['data'] = {
                'faceCount': face_count,
                'registered': registered['faceregistered'] if registered else 0,
                'dbFaceCount': registered['facecount'] if registered else 0
            }
        return JsonResponse(msg)

def face_match_api(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        face1_b64 = req_dict.get('face1') or req_dict.get('faceA')
        face2_b64 = req_dict.get('face2') or req_dict.get('faceB')
        if not face1_b64 or not face2_b64:
            msg['code'] = 400
            msg['msg'] = '请上传两张人脸图片'
            return JsonResponse(msg)
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        score, error, detail = ocv.match_face_from_base64(face1_b64, face2_b64)
        if error:
            msg['code'] = 500
            msg['msg'] = error
            return JsonResponse(msg)
        msg['data'] = detail
        return JsonResponse(msg)

def face_quality_check(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        face_b64 = req_dict.get('face') or req_dict.get('image')
        if not face_b64:
            msg['code'] = 400
            msg['msg'] = '请上传图片'
            return JsonResponse(msg)
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        try:
            score, details = ocv.check_quality_from_base64(face_b64)
        except Exception as e:
            print(f"质量检测异常: {e}")
            msg['code'] = 200
            msg['data'] = {'score': 0, 'details': {'error': str(e), 'clarity': 0, 'brightness': '异常', 'size': '异常', 'count': '异常'}}
            return JsonResponse(msg)
        if isinstance(details, str):
            msg['code'] = 200
            msg['data'] = {'score': 0, 'details': {'error': details, 'clarity': 0, 'brightness': '未检测到人脸', 'size': '-', 'count': '-'}}
            return JsonResponse(msg)
        msg['data'] = {'score': score, 'details': details}
        return JsonResponse(msg)

def system_config_get(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": []}
        configs = systemconfig.objects.all()
        for c in configs:
            msg['data'].append({
                'id': c.id,
                'configkey': c.configkey,
                'configvalue': c.configvalue,
                'description': c.description,
                'addtime': c.addtime.strftime('%Y-%m-%d %H:%M:%S') if c.addtime else ''
            })
        return JsonResponse(msg)

def system_config_set(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "配置已更新"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        configkey = req_dict.get('configkey')
        configvalue = req_dict.get('configvalue')
        if not configkey or configvalue is None:
            msg['code'] = 400
            msg['msg'] = '缺少参数'
            return JsonResponse(msg)
        obj = systemconfig.objects.filter(configkey=configkey).first()
        if obj:
            obj.configvalue = str(configvalue)
            obj.save()
        else:
            systemconfig.objects.create(configkey=configkey, configvalue=str(configvalue), description='')
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        current_threshold = ocv.get_threshold()
        msg['data'] = {'currentThreshold': current_threshold}
        return JsonResponse(msg)

def save_threshold(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "阈值已保存并生效"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        threshold = req_dict.get('threshold')
        if not threshold:
            msg['code'] = 400
            msg['msg'] = '缺少阈值参数'
            return JsonResponse(msg)
        try:
            threshold_val = int(threshold)
            if threshold_val < 40 or threshold_val > 100:
                msg['code'] = 400
                msg['msg'] = '阈值必须在40-100之间'
                return JsonResponse(msg)
            from util.opencv_face import OpenCVFace
            ocv = OpenCVFace()
            ocv.set_threshold(threshold_val)
            obj = systemconfig.objects.filter(configkey='face_threshold').first()
            if obj:
                obj.configvalue = str(threshold_val)
                obj.save()
            else:
                systemconfig.objects.create(configkey='face_threshold', configvalue=str(threshold_val), description='人脸识别匹配阈值')
            msg['data'] = {'threshold': threshold_val}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def delete_account(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp
        msg = {"code": normal_code, "msg": "删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        user_id = req_dict.get('id')
        is_admin_account = req_dict.get('_isAdmin', False) == True or req_dict.get('_isAdmin') == 'true'
        if not user_id:
            msg['code'] = 400
            msg['msg'] = '缺少用户ID'
            return JsonResponse(msg)
        try:
            uid = int(user_id)
            if is_admin_account:
                u = users.objects.filter(id=uid).first()
                if u:
                    from util.opencv_face import OpenCVFace
                    OpenCVFace().delete_user_faces(uid)
                    loginrecord.objects.filter(username=u.username).delete()
                    u.delete()
                    msg['data'] = {'deletedId': uid, 'account': u.username}
                else:
                    msg['code'] = 404
                    msg['msg'] = '管理员账号不存在'
            else:
                u = yonghu.objects.filter(id=uid).first()
                if u:
                    from util.opencv_face import OpenCVFace
                    OpenCVFace().delete_user_faces(uid)
                    loginrecord.objects.filter(username=u.yonghuzhanghao).delete()
                    u.delete()
                    msg['data'] = {'deletedId': uid, 'account': u.yonghuzhanghao}
                else:
                    msg['code'] = 404
                    msg['msg'] = '用户账号不存在'
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def batch_delete_accounts(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp
        msg = {"code": normal_code, "msg": "批量删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        ids_raw = req_dict.get('ids', '')
        if not ids_raw:
            msg['code'] = 400
            msg['msg'] = '缺少账号ID列表'
            return JsonResponse(msg)
        try:
            parts = ids_raw.split(',')
            items_to_delete = []
            for p in parts:
                p = p.strip()
                if '|' in p:
                    sid, sadmin = p.split('|', 1)
                    items_to_delete.append((int(sid), sadmin == '1'))
                elif p.isdigit():
                    items_to_delete.append((int(p), False))
            deleted_count = 0
            deleted_accounts = []
            from util.opencv_face import OpenCVFace
            ocv = OpenCVFace()
            for uid, is_admin_flag in items_to_delete:
                try:
                    if is_admin_flag:
                        au = users.objects.filter(id=uid).first()
                        if au:
                            ocv.delete_user_faces(uid)
                            loginrecord.objects.filter(username=au.username).delete()
                            deleted_accounts.append(au.username)
                            au.delete()
                            deleted_count += 1
                    else:
                        yu = yonghu.objects.filter(id=uid).first()
                        if yu:
                            ocv.delete_user_faces(uid)
                            loginrecord.objects.filter(username=yu.yonghuzhanghao).delete()
                            deleted_accounts.append(yu.yonghuzhanghao)
                            yu.delete()
                            deleted_count += 1
                except Exception as ex:
                    print(f'删除账号{uid}异常: {ex}')
            msg['data'] = {'deletedCount': deleted_count, 'accounts': deleted_accounts}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def dashboard_data(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {}}
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        stats = ocv.get_stats()
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        total_logins = loginrecord.objects.count()
        today_logins = loginrecord.objects.filter(addtime__gte=today).count()
        success_count = loginrecord.objects.filter(result='成功').count()
        fail_count = loginrecord.objects.filter(result='失败').count()
        stranger_result_count = loginrecord.objects.filter(result='陌生人').count()

        yonghu_total = yonghu.objects.count()
        admin_total = users.objects.count()
        total_users = yonghu_total + admin_total

        yonghu_registered = yonghu.objects.filter(faceregistered=1).count()
        admin_registered = 0
        admin_faces = 0
        for au in users.objects.all().values('id'):
            dr, dc = _get_face_status_from_disk(au['id'])
            if dr:
                admin_registered += 1
            admin_faces += dc

        registered_users = yonghu_registered + admin_registered
        unregistered_users = total_users - registered_users

        yonghu_faces = sum([u.facecount or 0 for u in yonghu.objects.all()])
        total_faces = yonghu_faces + admin_faces

        stranger_alerts = loginrecord.objects.filter(isstranger=1, result='陌生人').count()
        recent_logins = loginrecord.objects.order_by('-id')[:10]
        recent_list = []
        for r in recent_logins:
            recent_list.append({
                'id': r.id,
                'username': r.username,
                'role': r.role,
                'logintype': r.logintype,
                'result': r.result,
                'score': r.score,
                'addtime': r.addtime.strftime('%Y-%m-%d %H:%M:%S') if r.addtime else '',
            })
        from django.db.models import Count
        login_by_type = list(loginrecord.objects.values('logintype').annotate(count=Count('id')))
        login_by_role = list(loginrecord.objects.values('role').annotate(count=Count('id')))
        login_by_result = list(loginrecord.objects.values('result').annotate(count=Count('id')))
        success_rate = 0
        if total_logins > 0:
            success_rate = round((success_count / total_logins) * 100, 1)
        msg['data'] = {
            'faceStats': stats,
            'totalLogins': total_logins,
            'todayLogins': today_logins,
            'totalUsers': total_users,
            'yonghuTotal': yonghu_total,
            'adminTotal': admin_total,
            'registeredUsers': registered_users,
            'unregisteredUsers': unregistered_users,
            'totalFaces': total_faces,
            'strangerAlerts': stranger_alerts,
            'recentLogins': recent_list,
            'loginByType': login_by_type,
            'loginByRole': login_by_role,
            'loginByResult': login_by_result,
            'threshold': stats.get('threshold', 70),
            'successCount': success_count,
            'failCount': fail_count,
            'successRate': success_rate,
        }
        return JsonResponse(msg)

def face_detect_demo(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        face_b64 = req_dict.get('face') or req_dict.get('image')
        if not face_b64:
            msg['code'] = 400
            msg['msg'] = '请上传图片'
            return JsonResponse(msg)
        from util.opencv_face import OpenCVFace
        import cv2
        import numpy as np
        ocv = OpenCVFace()
        t_start = time.time()
        img_data = base64.b64decode(face_b64.split(',')[1] if ',' in face_b64 else face_b64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            msg['code'] = 400
            msg['msg'] = '无法解析图片'
            return JsonResponse(msg)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = ocv.face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3, minSize=(20, 20), maxSize=(300, 300))
        t_detect = time.time() - t_start
        face_boxes = []
        for (x, y, w, h) in faces:
            face_boxes.append({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)})
        msg['data'] = {
            'detected': len(faces) > 0,
            'faceCount': len(faces),
            'faces': face_boxes,
            'imageSize': {'width': img.shape[1], 'height': img.shape[0]},
            'detectTimeMs': round(t_detect * 1000, 1),
            'time': round(t_detect * 1000, 1),
        }
        return JsonResponse(msg)

def face_recognize_stranger(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        face_b64 = req_dict.get('face')
        if not face_b64:
            msg['code'] = 400
            msg['msg'] = '请上传人脸图片'
            return JsonResponse(msg)
        ip_addr = _get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')[:200]
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        threshold = ocv.get_threshold()
        face_path_saved = _save_face_image(face_b64)
        best_match_user = None
        best_score = 0
        all_scores = []
        scanned_count = 0
        try:
            matches, error, detail_info = ocv.match_all_registered_faces(face_b64)
            scanned_count = detail_info.get('total_users_checked', 0) if detail_info else 0
            if error:
                print(f'陌生人检测识别异常: {error}')
            user_ids = [m['user_id'] for m in matches] if matches else []
            user_map = {}
            if user_ids:
                user_objs = yonghu.objects.filter(id__in=user_ids).all()
                user_map = {u.id: u for u in user_objs}
            for m in (matches or []):
                uid = m['user_id']
                u = user_map.get(uid)
                username = u.yonghuzhanghao if u else f"用户{uid}"
                score = m['score']
                all_scores.append({'userId': uid, 'username': username, 'score': score, 'match': m['match']})
                if score > best_score:
                    best_score = score
                    best_match_user = {'id': uid, 'yonghuzhanghao': username}
        except Exception as e:
            print(f'陌生人检测异常: {e}')
            import traceback; traceback.print_exc()
        is_stranger = best_score < threshold
        if is_stranger and best_match_user is None:
            _save_login_record(
                username='未知访客',
                role='游客',
                logintype='人脸',
                score=best_score if best_score > 0 else 0,
                ipaddr=ip_addr,
                useragent=ua,
                result='陌生人',
                faceimage=face_path_saved,
                isstranger=1
            )
        msg['data'] = {
            'isStranger': is_stranger,
            'bestScore': best_score,
            'threshold': threshold,
            'bestMatch': {
                'userId': best_match_user['id'],
                'username': best_match_user['yonghuzhanghao'],
                'score': best_score,
            } if best_match_user else None,
            'allScores': sorted(all_scores, key=lambda x: x['score'], reverse=True)[:5],
            'scannedCount': scanned_count,
        }
        return JsonResponse(msg)

def change_password(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "密码修改成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        old_pwd = req_dict.get('oldPassword')
        new_pwd = req_dict.get('newPassword')
        userid = req_dict.get('userid')
        if not old_pwd or not new_pwd or not userid:
            msg['code'] = 400
            msg['msg'] = '缺少必要参数'
            return JsonResponse(msg)
        try:
            user = yonghu.objects.filter(id=int(userid)).first()
            if not user:
                user = users.objects.filter(id=int(userid)).first()
            if not user:
                msg['code'] = 404
                msg['msg'] = '用户不存在'
                return JsonResponse(msg)
            pwd_field = 'mima' if hasattr(user, 'mima') else 'password'
            old_pwd_val = getattr(user, pwd_field, '')
            if old_pwd_val != old_pwd:
                msg['code'] = 401
                msg['msg'] = '原密码错误'
                return JsonResponse(msg)
            setattr(user, pwd_field, new_pwd)
            if hasattr(user, 'mustchangepwd'):
                user.mustchangepwd = 0
            user.save()
            msg['data'] = {'success': True}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def user_profile_get(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {}}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        userid = req_dict.get('userid')
        if not userid:
            msg['code'] = 400
            msg['msg'] = '缺少用户ID'
            return JsonResponse(msg)
        user = yonghu.objects.filter(id=int(userid)).first()
        if not user:
            user = users.objects.filter(id=int(userid)).first()
        if not user:
            msg['code'] = 404
            msg['msg'] = '用户不存在'
            return JsonResponse(msg)
        from util.opencv_face import OpenCVFace
        ocv = OpenCVFace()
        face_count = ocv.get_face_count(int(userid))
        is_yonghu = hasattr(user, 'yonghuzhanghao')
        if is_yonghu:
            msg['data'] = {
                'id': user.id,
                'yonghuzhanghao': user.yonghuzhanghao,
                'yonghuxingming': user.yonghuxingming,
                'lianxidianhua': user.lianxidianhua,
                'xingbie': user.xingbie,
                'touxiang': user.touxiang or '',
                'faceregistered': user.faceregistered or 0,
                'facecount': face_count,
                'addtime': user.addtime.strftime('%Y-%m-%d %H:%M:%S') if user.addtime else '',
            }
        else:
            msg['data'] = {
                'id': user.id,
                'yonghuzhanghao': getattr(user, 'username', 'admin'),
                'yonghuxingming': getattr(user, 'name', '管理员'),
                'lianxidianhua': '',
                'xingbie': '',
                'touxiang': getattr(user, 'touxiang', '') or '',
                'faceregistered': 0,
                'facecount': 0,
                'addtime': '',
            }
        return JsonResponse(msg)

def _check_auth(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header:
        return False, None
    try:
        token_str = auth_header.replace('Bearer ', '').strip()
        if not token_str:
            return False, None
        import base64
        decoded = base64.b64decode(token_str).decode('utf-8')
        payload = eval(decoded)
        if payload and 'params' in payload:
            return True, payload
        return False, None
    except Exception as e:
        print(f'认证检查失败: {e}')
        return False, None

def _require_admin(request):
    is_auth, payload = _check_auth(request)
    if not is_auth:
        return False, JsonResponse({"code": 401, "msg": "未包含认证信息，请先登录"})
    tablename = payload.get('tablename', '')
    if tablename != 'users':
        return False, JsonResponse({"code": 403, "msg": "权限不足：仅管理员可执行删除操作"})
    return True, None

def delete_login_record(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp
        
        msg = {"code": normal_code, "msg": "删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        record_id = req_dict.get('id')
        if not record_id:
            msg['code'] = 400
            msg['msg'] = '缺少记录ID'
            return JsonResponse(msg)
        try:
            record = loginrecord.objects.filter(id=int(record_id)).first()
            if not record:
                msg['code'] = 404
                msg['msg'] = '记录不存在'
                return JsonResponse(msg)
            if record.faceimage:
                try:
                    img_path = os.path.join(os.getcwd(), "templates", record.faceimage.lstrip('/'))
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except:
                    pass
            record.delete()
            msg['data'] = {'deleted': True}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def batch_delete_records(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp

        msg = {"code": normal_code, "msg": "批量删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        ids_str = req_dict.get('ids', '')
        if not ids_str:
            msg['code'] = 400
            msg['msg'] = '缺少记录ID列表'
            return JsonResponse(msg)
        try:
            ids = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
            deleted_count = 0
            for rid in ids:
                record = loginrecord.objects.filter(id=rid).first()
                if record:
                    if record.faceimage:
                        try:
                            img_path = os.path.join(os.getcwd(), "templates", record.faceimage.lstrip('/'))
                            if os.path.exists(img_path):
                                os.remove(img_path)
                        except:
                            pass
                    record.delete()
                    deleted_count += 1
            msg['data'] = {'deletedCount': deleted_count}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def delete_stranger_record(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp
        msg = {"code": normal_code, "msg": "删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        record_id = req_dict.get('id')
        if not record_id:
            msg['code'] = 400
            msg['msg'] = '缺少记录ID'
            return JsonResponse(msg)
        try:
            record = loginrecord.objects.filter(id=int(record_id), isstranger=1).first()
            if not record:
                msg['code'] = 404
                msg['msg'] = '告警记录不存在'
                return JsonResponse(msg)
            if record.faceimage:
                try:
                    img_path = os.path.join(os.getcwd(), "templates", record.faceimage.lstrip('/'))
                    if os.path.exists(img_path):
                        os.remove(img_path)
                except:
                    pass
            record.delete()
            msg['data'] = {'deleted': True}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def batch_delete_stranger_records(request):
    if request.method in ["POST", "GET"]:
        is_admin, err_resp = _require_admin(request)
        if not is_admin:
            return err_resp
        msg = {"code": normal_code, "msg": "批量删除成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        ids_str = req_dict.get('ids', '')
        if not ids_str:
            msg['code'] = 400
            msg['msg'] = '缺少记录ID列表'
            return JsonResponse(msg)
        try:
            ids = [int(x.strip()) for x in ids_str.split(',') if x.strip().isdigit()]
            deleted_count = 0
            for rid in ids:
                record = loginrecord.objects.filter(id=rid, isstranger=1).first()
                if record:
                    if record.faceimage:
                        try:
                            img_path = os.path.join(os.getcwd(), "templates", record.faceimage.lstrip('/'))
                            if os.path.exists(img_path):
                                os.remove(img_path)
                        except:
                            pass
                    record.delete()
                    deleted_count += 1
            msg['data'] = {'deletedCount': deleted_count}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def stranger_alert_list(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {"list": []}}
        records = loginrecord.objects.filter(
            isstranger=1, 
            result='陌生人',
            logintype='人脸'
        ).order_by('-id')[:50]
        for r in records:
            msg['data']['list'].append({
                'id': r.id,
                'addtime': r.addtime.strftime('%Y-%m-%d %H:%M:%S') if r.addtime else '',
                'username': r.username,
                'score': r.score,
                'ipaddress': r.ipaddress,
                'faceimage': r.faceimage,
                'useragent': (r.useragent[:100] + '..') if r.useragent and len(r.useragent) > 100 else (r.useragent or ''),
            })
        return JsonResponse(msg)

def update_user_avatar(request):
    if request.method in ["POST", "GET"]:
        is_auth, _ = _check_auth(request)
        if not is_auth:
            return JsonResponse({"code": 401, "msg": "未包含认证信息，请先登录"})
        
        msg = {"code": normal_code, "msg": "头像更新成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        userid = req_dict.get('userid')
        avatar_b64 = req_dict.get('avatar')
        if not userid or not avatar_b64:
            msg['code'] = 400
            msg['msg'] = '缺少参数'
            return JsonResponse(msg)
        try:
            is_admin = req_dict.get('_isAdmin', False)
            user = None
            if is_admin:
                user = users.objects.filter(id=int(userid)).first()
            else:
                user = yonghu.objects.filter(id=int(userid)).first()
            if not user:
                msg['code'] = 404
                msg['msg'] = '用户不存在'
                return JsonResponse(msg)
            upload_dir = os.path.join(os.getcwd(), "templates", "file", "avatars")
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            filename = f"avatar_{userid}_{int(time.time())}.jpg"
            filepath = os.path.join(upload_dir, filename)
            if ',' in avatar_b64:
                b64data = avatar_b64.split(',')[1]
            else:
                b64data = avatar_b64
            img_data = base64.b64decode(b64data)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            avatar_url = f"/file/avatars/{filename}"
            user.touxiang = avatar_url
            user.save()
            msg['data'] = {'avatar': avatar_url}
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def update_user_profile(request):
    if request.method in ["POST", "GET"]:
        is_auth, _ = _check_auth(request)
        if not is_auth:
            return JsonResponse({"code": 401, "msg": "未包含认证信息，请先登录"})
        
        msg = {"code": normal_code, "msg": "信息更新成功"}
        req_dict = request.session.get("req_dict") or {}
        if request.method == 'POST' and request.content_type and 'application/json' in request.content_type:
            try:
                req_dict = json.loads(request.body)
            except:
                pass
        elif request.method == 'POST':
            post_data = request.POST.dict()
            req_dict.update(post_data)
        userid = req_dict.get('userid')
        if not userid:
            msg['code'] = 400
            msg['msg'] = '缺少用户ID'
            return JsonResponse(msg)
        try:
            user = yonghu.objects.filter(id=int(userid)).first()
            if not user:
                user = users.objects.filter(id=int(userid)).first()
            if not user:
                msg['code'] = 404
                msg['msg'] = '用户不存在，请重新登录'
                return JsonResponse(msg)
            is_yonghu = hasattr(user, 'yonghuzhanghao')
            updated = False
            if 'yonghuxingming' in req_dict and is_yonghu:
                name = req_dict['yonghuxingming'].strip()
                if name and len(name) <= 20:
                    existing = yonghu.objects.filter(yonghuzhanghao=name).exclude(id=int(userid)).first()
                    if existing:
                        msg['code'] = 400
                        msg['msg'] = '该名称已被使用，请选择其他名称'
                        return JsonResponse(msg)
                    user.yonghuxingming = name
                    updated = True
                elif len(name) > 20:
                    msg['code'] = 400
                    msg['msg'] = '名称不能超过20个字符'
                    return JsonResponse(msg)
            if 'lianxidianhua' in req_dict:
                user.lianxidianhua = req_dict['lianxidianhua']
                updated = True
            if 'xingbie' in req_dict:
                xingbie_val = req_dict['xingbie']
                if xingbie_val in ['男', '女', '保密']:
                    user.xingbie = xingbie_val
                    updated = True
            if updated:
                user.save()
                msg['data'] = {
                    'yonghuzhanghao': user.yonghuzhanghao,
                    'yonghuxingming': user.yonghuxingming,
                    'lianxidianhua': user.lianxidianhua,
                    'xingbie': user.xingbie,
                    'id': user.id,
                }
            else:
                msg['msg'] = '没有需要更新的字段'
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def face_history_page(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {"list": [], "currPage": 1, "totalPage": 1, "total": 0, "pageSize": 10}}
        records = faceregister.objects.filter(isvalid=1).order_by('-id')[:20]
        for r in records:
            msg['data']['list'].append({
                'id': r.id,
                'userid': r.userid,
                'username': r.username,
                'regtime': r.regtime.strftime('%Y-%m-%d %H:%M:%S') if r.regtime else '',
                'faceimage': r.faceimage,
                'qualityscore': r.qualityscore,
            })
        return JsonResponse(msg)

def face_reg_list(request):
    if request.method in ["POST", "GET"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {"list": []}}
        records = faceregister.objects.filter(isvalid=1).order_by('-id')[:30]
        for r in records:
            msg['data']['list'].append({
                'id': r.id,
                'userid': r.userid,
                'username': r.username,
                'regtime': r.regtime.strftime('%Y-%m-%d %H:%M:%S') if r.regtime else '',
            })
        return JsonResponse(msg)

def _get_face_status_from_disk(user_id):
    train_dir = os.path.join(os.getcwd(), "templates", "file", "face_train", str(user_id))
    if os.path.exists(train_dir):
        count = len([f for f in os.listdir(train_dir) if f.endswith('.pgm') or f.endswith('.jpg')])
        if count > 0:
            return 1, count
    return 0, 0

def all_registered_accounts(request):
    if request.method in ["GET", "POST"]:
        msg = {"code": normal_code, "msg": "操作成功", "data": {"list": [], "total": 0}}
        try:
            admin_list = []
            for u in users.objects.all().values('id', 'username', 'role', 'addtime'):
                item = dict(u)
                item['yonghuzhanghao'] = item.get('username', '')
                item['yonghuxingming'] = item.get('role', '管理员')
                db_reg = int(item.get('faceregistered', 0) or 0)
                disk_reg, disk_count = _get_face_status_from_disk(item['id'])
                item['faceregistered'] = max(db_reg, disk_reg)
                item['facecount'] = max(int(item.get('facecount', 0) or 0), disk_count)
                item['_isAdmin'] = True
                item['_roleTag'] = '管理员'
                admin_list.append(item)

            user_list = []
            for y in yonghu.objects.all().values('id', 'yonghuzhanghao', 'yonghuxingming', 'touxiang',
                                                  'xingbie', 'lianxidianhua', 'faceregistered', 'facecount', 'addtime'):
                item = dict(y)
                disk_reg, disk_count = _get_face_status_from_disk(item['id'])
                if disk_count > 0 and not item.get('faceregistered'):
                    item['faceregistered'] = 1
                    item['facecount'] = max(item.get('facecount', 0), disk_count)
                item['_isAdmin'] = False
                item['_roleTag'] = '普通用户'
                user_list.append(item)

            all_accounts = admin_list + user_list

            search = request.GET.get('search', '').strip()
            reg_filter = request.GET.get('faceregistered', '')

            if search:
                s = search.lower()
                all_accounts = [a for a in all_accounts if
                                (a.get('yonghuzhanghao') and s in a['yonghuzhanghao'].lower()) or
                                (a.get('yonghuxingming') and s in str(a['yonghuxingming']).lower())]

            if reg_filter != '':
                rv = int(reg_filter)
                all_accounts = [a for a in all_accounts if (1 if a.get('faceregistered') else 0) == rv]

            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            total = len(all_accounts)
            start = (page - 1) * limit
            page_data = all_accounts[start:start + limit]
            total_page = (total + limit - 1) // limit if total > 0 else 1

            msg['data']['list'] = page_data
            msg['data']['total'] = total
            msg['data']['totalPage'] = total_page
            msg['data']['currPage'] = page
        except Exception as e:
            print(f'all_registered_accounts error: {e}')
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)

def update_account_name(request):
    if request.method in ["POST"]:
        msg = {"code": normal_code, "msg": "修改成功", "data": {}}
        try:
            body = json.loads(request.body)
            user_id = body.get('id')
            is_admin = body.get('_isAdmin', False)
            new_account = body.get('yonghuzhanghao', '').strip()
            new_name = body.get('yonghuxingming', '').strip()

            if not new_account:
                msg['code'] = 400
                msg['msg'] = '账号不能为空'
                return JsonResponse(msg)

            if is_admin:
                u = users.objects.filter(id=user_id).first()
                if u:
                    old_name = u.username
                    u.username = new_account
                    if new_name:
                        u.role = new_name
                    u.save()
                    loginrecord.objects.filter(username=old_name).update(username=new_account)
                    msg['data'] = {'oldAccount': old_name, 'newAccount': new_account}
                else:
                    msg['code'] = 404
                    msg['msg'] = '用户不存在'
            else:
                u = yonghu.objects.filter(id=user_id).first()
                if u:
                    old_account = u.yonghuzhanghao
                    old_name = u.yonghuxingming
                    u.yonghuzhanghao = new_account
                    if new_name:
                        u.yonghuxingming = new_name
                    u.save()
                    loginrecord.objects.filter(username=old_account).update(username=new_account)
                    msg['data'] = {'oldAccount': old_account, 'newAccount': new_account}
                else:
                    msg['code'] = 404
                    msg['msg'] = '用户不存在'
        except Exception as e:
            msg['code'] = 500
            msg['msg'] = str(e)
        return JsonResponse(msg)
