#coding:utf-8
__author__ = "ila"

import cv2
import os
import numpy as np
import json
import base64
import time
from PIL import Image
import io

class OpenCVFace(object):

    def __init__(self):
        self.cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(self.cascade_path)
        if not hasattr(cv2, 'face'):
            raise RuntimeError(
                '缺少 OpenCV 人脸识别模块，请安装: pip install opencv-contrib-python'
            )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        self.train_data_dir = os.path.join(os.getcwd(), "templates", "file", "face_train")
        if not os.path.exists(self.train_data_dir):
            os.makedirs(self.train_data_dir)
        self.trained = False
        self.default_threshold = 70

    def _db_conn(self):
        import pymysql
        from util.configread import config_read
        ini = os.path.join(os.getcwd(), 'config.ini')
        if not os.path.isfile(ini):
            return None
        _t, host, port, user, passwd, db, charset = config_read(ini)
        if not db:
            return None
        return pymysql.connect(
            host=host, port=int(port), user=user, password=passwd,
            database=db.replace(' ', '').strip(), charset='utf8mb4'
        )

    def get_threshold(self):
        try:
            conn = self._db_conn()
            if not conn:
                return self.default_threshold
            cur = conn.cursor()
            cur.execute("SELECT configvalue FROM systemconfig WHERE configkey='face_threshold'")
            row = cur.fetchone()
            conn.close()
            if row:
                val = float(row[0])
                return max(40, min(100, val))
        except Exception:
            pass
        return self.default_threshold

    def set_threshold(self, value):
        try:
            value = max(40, min(100, float(value)))
            conn = self._db_conn()
            if not conn:
                return False
            cur = conn.cursor()
            cur.execute("UPDATE systemconfig SET configvalue=%s WHERE configkey='face_threshold'", (str(value),))
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def _detect_faces(self, gray):
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.08, minNeighbors=7,
            minSize=(60, 60), maxSize=(int(gray.shape[1]*0.8), int(gray.shape[0]*0.8))
        )
        return faces

    def _select_best_face(self, faces, img_shape):
        if len(faces) == 0:
            return None
        if len(faces) == 1:
            return tuple(faces[0])

        h_img, w_img = img_shape[:2]
        center_x, center_y = w_img / 2, h_img / 2

        scored = []
        for (x, y, w, h) in faces:
            aspect = float(w) / max(float(h), 1)
            if aspect < 0.5 or aspect > 2.0:
                continue
            area = w * h
            cx, cy = x + w/2, y + h/2
            dist_center = ((cx - center_x)**2 + (cy - center_y)**2) ** 0.5
            max_dist = (w_img**2 + h_img**2) ** 0.5
            center_score = max(0, 1 - dist_center / max_dist)
            size_score = min(1, area / (w_img * h_img * 0.05))
            total = area * (0.4 + center_score * 0.5 + size_score * 0.1)
            scored.append((total, x, y, w, h))

        if not scored:
            return max(faces, key=lambda f: f[2]*f[3])
        scored.sort(key=lambda s: s[0], reverse=True)
        return (scored[0][1], scored[0][2], scored[0][3], scored[0][4])

    def _base64_to_image(self, base64_str):
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return img

    def _image_to_base64(self, image_path):
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def check_quality(self, image_path):
        try:
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return 0, "无法读取图片"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._detect_faces(gray)
            best = self._select_best_face(faces, img.shape)
            if best is None:
                return 0, "未检测到人脸"
            x, y, w, h = best
            face_region = gray[y:y+h, x:x+w]
            laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()
            brightness = np.mean(face_region)
            face_ratio = (w * h) / (img.shape[0] * img.shape[1])
            score = 0
            details = {}
            clarity_score = min(100, max(0, laplacian_var / 10))
            details['clarity'] = round(clarity_score, 1)
            if clarity_score > 100:
                score += 35
            elif clarity_score > 50:
                score += 25
            elif clarity_score > 20:
                score += 15
            else:
                score += 5
            if 60 <= brightness <= 200:
                score += 25
                details['brightness'] = '正常'
            elif 30 <= brightness < 60 or 200 < brightness <= 240:
                score += 15
                details['brightness'] = '偏暗' if brightness < 60 else '偏亮'
            else:
                score += 5
                details['brightness'] = '过暗' if brightness < 30 else '过亮'
            if face_ratio >= 0.1:
                score += 25
                details['size'] = '合适'
            elif face_ratio >= 0.05:
                score += 15
                details['size'] = '偏小'
            else:
                score += 5
                details['size'] = '过小'
            if len(faces) == 1:
                score += 15
                details['count'] = '单人'
            else:
                score += 5
                details['count'] = f'{len(faces)}人'
            score = min(100, max(0, score))
            details['total'] = round(score, 1)
            details['laplacian'] = round(laplacian_var, 1)
            details['brightness_val'] = round(brightness, 1)
            details['face_ratio'] = round(face_ratio, 4)
            return score, details
        except Exception as e:
            return 0, str(e)

    def check_quality_from_base64(self, base64_str):
        try:
            img = self._base64_to_image(base64_str)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._detect_faces(gray)
            best = self._select_best_face(faces, img.shape)
            if best is None:
                return 0, "未检测到人脸"
            x, y, w, h = best
            face_region = gray[y:y+h, x:x+w]
            laplacian_var = cv2.Laplacian(face_region, cv2.CV_64F).var()
            brightness = np.mean(face_region)
            face_ratio = (w * h) / (img.shape[0] * img.shape[1])
            score = 0
            details = {}
            clarity_score = min(100, max(0, laplacian_var / 10))
            details['clarity'] = round(clarity_score, 1)
            if clarity_score > 100:
                score += 35
            elif clarity_score > 50:
                score += 25
            elif clarity_score > 20:
                score += 15
            else:
                score += 5
            if 60 <= brightness <= 200:
                score += 25
                details['brightness'] = '正常'
            elif 30 <= brightness < 60 or 200 < brightness <= 240:
                score += 15
                details['brightness'] = '偏暗' if brightness < 60 else '偏亮'
            else:
                score += 5
                details['brightness'] = '过暗' if brightness < 30 else '过亮'
            if face_ratio >= 0.1:
                score += 25
                details['size'] = '合适'
            elif face_ratio >= 0.05:
                score += 15
                details['size'] = '偏小'
            else:
                score += 5
                details['size'] = '过小'
            if len(faces) == 1:
                score += 15
                details['count'] = '单人'
            else:
                score += 5
                details['count'] = f'{len(faces)}人'
            score = min(100, max(0, score))
            details['total'] = round(score, 1)
            details['laplacian'] = round(laplacian_var, 1)
            details['brightness_val'] = round(brightness, 1)
            details['face_ratio'] = round(face_ratio, 4)
            return score, details
        except Exception as e:
            return 0, str(e)

    def detect_face(self, image_path):
        try:
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return None, None, "无法读取图片"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._detect_faces(gray)
            best = self._select_best_face(faces, img.shape)
            if best is None:
                return None, None, "未检测到人脸"
            x, y, w, h = best
            face_gray = gray[y:y+h, x:x+w]
            face_gray = cv2.resize(face_gray, (200, 200))
            face_color = img[y:y+h, x:x+w]
            face_color = cv2.resize(face_color, (200, 200))
            return face_gray, face_color, None
        except Exception as e:
            return None, None, str(e)

    def detect_face_with_info(self, image_path):
        try:
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                return None, None, "无法读取图片"
            t_start = time.time()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._detect_faces(gray)
            t_detect = time.time() - t_start
            best = self._select_best_face(faces, img.shape)
            if best is None:
                return None, None, "未检测到人脸"
            x, y, w, h = best
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, (200, 200))
            info = {
                'detect_time_ms': round(t_detect * 1000, 1),
                'face_count': len(faces),
                'face_position': {'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)},
                'image_size': {'width': img.shape[1], 'height': img.shape[0]},
                'face_size': {'width': int(w), 'height': int(h)}
            }
            return face_img, info, None
        except Exception as e:
            return None, None, str(e)

    def detect_face_from_base64(self, base64_str):
        try:
            img = self._base64_to_image(base64_str)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._detect_faces(gray)
            best = self._select_best_face(faces, img.shape)
            if best is None:
                return None, None, "未检测到人脸"
            x, y, w, h = best
            face_gray = gray[y:y+h, x:x+w]
            face_gray = cv2.resize(face_gray, (200, 200))
            face_color = img[y:y+h, x:x+w]
            face_color = cv2.resize(face_color, (200, 200))
            return face_gray, face_color, None
        except Exception as e:
            return None, None, str(e)

    def register_face(self, user_id, image_path):
        try:
            quality, qdetails = self.check_quality(image_path)
            if isinstance(qdetails, str):
                return False, qdetails
            if quality < 40:
                return False, f"图片质量过低({quality}分)，请重新拍摄清晰正面照片"
            face_gray, face_color, error = self.detect_face(image_path)
            if error:
                return False, error
            user_dir = os.path.join(self.train_data_dir, str(user_id))
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            count = len([f for f in os.listdir(user_dir) if f.endswith('.pgm')])
            save_path_pgm = os.path.join(user_dir, f"face_{count+1}.pgm")
            save_path_jpg = os.path.join(user_dir, f"face_{count+1}.jpg")
            display_path = os.path.join(user_dir, "display.jpg")
            cv2.imencode('.pgm', face_gray)[1].tofile(save_path_pgm)
            cv2.imencode('.jpg', face_color)[1].tofile(save_path_jpg)
            orig_img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
            if orig_img is not None:
                cv2.imencode('.jpg', orig_img)[1].tofile(display_path)
            self._retrain()
            return True, f"人脸注册成功(质量:{quality}分)"
        except Exception as e:
            return False, str(e)

    def register_face_from_base64(self, user_id, base64_str):
        try:
            quality, qdetails = self.check_quality_from_base64(base64_str)
            if isinstance(qdetails, str):
                return False, qdetails
            if quality < 40:
                return False, f"图片质量过低({quality}分)，请重新拍摄清晰正面照片"
            face_gray, face_color, error = self.detect_face_from_base64(base64_str)
            if error:
                return False, error
            user_dir = os.path.join(self.train_data_dir, str(user_id))
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            count = len([f for f in os.listdir(user_dir) if f.endswith('.pgm')])
            save_path_pgm = os.path.join(user_dir, f"face_{count+1}.pgm")
            save_path_jpg = os.path.join(user_dir, f"face_{count+1}.jpg")
            display_path = os.path.join(user_dir, "display.jpg")
            cv2.imencode('.pgm', face_gray)[1].tofile(save_path_pgm)
            cv2.imencode('.jpg', face_color)[1].tofile(save_path_jpg)
            orig_img = self._base64_to_image(base64_str)
            cv2.imencode('.jpg', orig_img)[1].tofile(display_path)
            self._retrain()
            return True, f"人脸注册成功(质量:{quality}分)"
        except Exception as e:
            return False, str(e)

    def _retrain(self):
        faces = []
        labels = []
        label_dict = {}
        current_label = 0
        if not os.path.exists(self.train_data_dir):
            return
        for user_id in os.listdir(self.train_data_dir):
            user_dir = os.path.join(self.train_data_dir, user_id)
            if not os.path.isdir(user_dir):
                continue
            label_dict[current_label] = int(user_id)
            for file_name in os.listdir(user_dir):
                if file_name.endswith('.pgm'):
                    file_path = os.path.join(user_dir, file_name)
                    img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        labels.append(current_label)
            current_label += 1
        if len(faces) > 0:
            self.recognizer.train(faces, np.array(labels))
            self.trained = True
            label_map_path = os.path.join(self.train_data_dir, "label_map.json")
            with open(label_map_path, 'w') as f:
                json.dump(label_dict, f)
            model_path = os.path.join(self.train_data_dir, "lbph_model.yml")
            try:
                self.recognizer.write(model_path)
                print(f'[OpenCVFace] 模型已保存到: {model_path} (样本数:{len(faces)}, 用户数:{current_label})')
            except Exception as e:
                print(f'[OpenCVFace] 模型保存失败: {e}')

    def match_face(self, image1_path, image2_path):
        try:
            t_start = time.time()
            face1, _, error1 = self.detect_face(image1_path)
            if error1:
                return 0, error1, {}
            face2, _, error2 = self.detect_face(image2_path)
            if error2:
                return 0, error2, {}
            face1_norm = face1.astype(np.float32) / 255.0
            face2_norm = face2.astype(np.float32) / 255.0
            diff = face1_norm - face2_norm
            score = float(np.mean(1.0 - np.abs(diff)))
            score = max(0.0, min(100.0, score * 100))
            t_total = time.time() - t_start
            result = {
                'score': round(score, 2),
                'threshold': self.get_threshold(),
                'match': score >= self.get_threshold(),
                'time_ms': round(t_total * 1000, 1),
                'level': self._get_score_level(score)
            }
            return round(score, 2), None, result
        except Exception as e:
            return 0, str(e), {}

    def compare_face_with_registered(self, base64_str, registered_face_path):
        try:
            t_start = time.time()
            login_face_gray, _, error = self.detect_face_from_base64(base64_str)
            if error:
                return 0, f"登录图片检测失败:{error}", {}
            reg_img = cv2.imdecode(np.fromfile(registered_face_path, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
            if reg_img is None:
                return 0, "无法读取注册人脸文件", {}
            if reg_img.shape != (200, 200):
                reg_img = cv2.resize(reg_img, (200, 200))
            login_norm = login_face_gray.astype(np.float32) / 255.0
            reg_norm = reg_img.astype(np.float32) / 255.0
            diff = login_norm - reg_norm
            score = float(np.mean(1.0 - np.abs(diff)))
            score = max(0.0, min(100.0, score * 100))
            t_total = time.time() - t_start
            result = {
                'score': round(score, 2),
                'threshold': self.get_threshold(),
                'match': score >= self.get_threshold(),
                'time_ms': round(t_total * 1000, 1),
                'level': self._get_score_level(score)
            }
            return round(score, 2), None, result
        except Exception as e:
            return 0, str(e), {}

    def match_all_registered_faces(self, base64_str):
        try:
            t_start = time.time()
            threshold = self.get_threshold()
            login_face_gray, _, detect_error = self.detect_face_from_base64(base64_str)
            if detect_error:
                return [], f"登录图片检测失败:{detect_error}", {}
            best_matches = []
            if not os.path.exists(self.train_data_dir):
                return [], "无注册数据", {'total_users_checked': 0}
            for user_id_str in os.listdir(self.train_data_dir):
                user_dir = os.path.join(self.train_data_dir, user_id_str)
                if not os.path.isdir(user_dir):
                    continue
                user_best_score = 0
                for fname in os.listdir(user_dir):
                    if not (fname.endswith('.pgm') or fname.endswith('.jpg')):
                        continue
                    fpath = os.path.join(user_dir, fname)
                    reg_img = cv2.imdecode(np.fromfile(fpath, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    if reg_img is None:
                        continue
                    if reg_img.shape != (200, 200):
                        reg_img = cv2.resize(reg_img, (200, 200))
                    login_norm = login_face_gray.astype(np.float32) / 255.0
                    reg_norm = reg_img.astype(np.float32) / 255.0
                    diff = login_norm - reg_norm
                    score = float(np.mean(1.0 - np.abs(diff)))
                    score = max(0.0, min(100.0, score * 100))
                    if score > user_best_score:
                        user_best_score = score
                if user_best_score > 0:
                    best_matches.append({
                        'user_id': int(user_id_str),
                        'score': round(user_best_score, 2),
                        'match': user_best_score >= threshold,
                        'level': self._get_score_level(user_best_score)
                    })
            best_matches.sort(key=lambda x: x['score'], reverse=True)
            t_total = time.time() - t_start
            result_info = {
                'total_users_checked': len(best_matches),
                'threshold': threshold,
                'time_ms': round(t_total * 1000, 1),
                'best_match': best_matches[0] if best_matches else None,
                'all_scores': [(m['user_id'], m['score']) for m in best_matches[:10]]
            }
            return best_matches, None, result_info
        except Exception as e:
            return [], str(e), {}

    def match_face_from_base64(self, base64_str1, base64_str2):
        try:
            t_start = time.time()
            face1, _, error1 = self.detect_face_from_base64(base64_str1)
            if error1:
                return 0, error1, {}
            face2, _, error2 = self.detect_face_from_base64(base64_str2)
            if error2:
                return 0, error2, {}
            face1_norm = face1.astype(np.float32) / 255.0
            face2_norm = face2.astype(np.float32) / 255.0
            diff = face1_norm - face2_norm
            score = float(np.mean(1.0 - np.abs(diff)))
            score = max(0.0, min(100.0, score * 100))
            t_total = time.time() - t_start
            result = {
                'score': round(score, 2),
                'threshold': self.get_threshold(),
                'match': score >= self.get_threshold(),
                'time_ms': round(t_total * 1000, 1),
                'level': self._get_score_level(score)
            }
            return round(score, 2), None, result
        except Exception as e:
            return 0, str(e), {}

    def recognize_face_login(self, base64_str):
        try:
            t_start = time.time()
            threshold = self.get_threshold()

            if not self.trained:
                print('[OpenCVFace] 模型未训练，尝试加载已保存的模型...')
                self._load_trainer()

            if not self.trained:
                print('[OpenCVFace] 无已保存模型，尝试重新训练...')
                self._retrain()

            if not self.trained:
                return None, "系统尚未训练，请先注册人脸", {}

            face_img, _, error = self.detect_face_from_base64(base64_str)
            if error:
                return None, error, {}

            label, confidence = self.recognizer.predict(face_img)
            score = max(0, min(100, (100 - confidence) * 1.5))

            t_total = time.time() - t_start
            label_map_path = os.path.join(self.train_data_dir, "label_map.json")

            if os.path.exists(label_map_path):
                with open(label_map_path, 'r') as f:
                    label_dict = json.load(f)
                user_id = label_dict.get(str(label))
                result = {
                    'user_id': user_id,
                    'score': round(score, 2),
                    'threshold': threshold,
                    'match': score >= threshold,
                    'confidence': round(confidence, 2),
                    'time_ms': round(t_total * 1000, 1),
                    'level': self._get_score_level(score)
                }
                print(f'[OpenCVFace] LBPH识别完成: user_id={user_id}, score={score:.2f}, threshold={threshold}, match={score >= threshold}')
                return result, None, result

            print(f'[OpenCVFace] 无法从label_map中找到用户: label={label}')
            return None, "无法识别用户身份", {}
        except Exception as e:
            print(f'[OpenCVFace] recognize_face_login异常: {e}')
            import traceback
            traceback.print_exc()
            return None, str(e), {}

    def _get_score_level(self, score):
        if score >= 85:
            return '高度匹配'
        elif score >= 70:
            return '匹配'
        elif score >= 50:
            return '低度相似'
        elif score >= 30:
            return '疑似同一人'
        else:
            return '非同一人'

    def _load_trainer(self):
        model_path = os.path.join(self.train_data_dir, "lbph_model.yml")
        label_map_path = os.path.join(self.train_data_dir, "label_map.json")
        if os.path.exists(model_path) and os.path.exists(label_map_path):
            try:
                self.recognizer.read(model_path)
                self.trained = True
            except:
                pass

    def get_face_count(self, user_id):
        user_dir = os.path.join(self.train_data_dir, str(user_id))
        if not os.path.exists(user_dir):
            return 0
        return len([f for f in os.listdir(user_dir) if f.endswith('.pgm')])

    def delete_user_faces(self, user_id):
        import shutil
        user_dir = os.path.join(self.train_data_dir, str(user_id))
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            self._retrain()

    def get_stats(self):
        stats = {
            'trained': self.trained,
            'threshold': self.get_threshold(),
            'total_users': 0,
            'total_faces': 0,
            'users_detail': []
        }
        if not os.path.exists(self.train_data_dir):
            return stats
        for user_id in os.listdir(self.train_data_dir):
            user_dir = os.path.join(self.train_data_dir, user_id)
            if os.path.isdir(user_dir):
                count = len([f for f in os.listdir(user_dir) if f.endswith('.pgm')])
                stats['total_users'] += 1
                stats['total_faces'] += count
                stats['users_detail'].append({'user_id': int(user_id), 'face_count': count})
        return stats

if __name__ == '__main__':
    of = OpenCVFace()
    print("OpenCV人脸识别模块初始化成功")
    print("Haar级联分类器路径:", of.cascade_path)
    print("训练数据目录:", of.train_data_dir)
    print("当前阈值:", of.get_threshold())
    print("统计:", json.dumps(of.get_stats(), ensure_ascii=False, indent=2))
