# coding:utf-8
__author__ = "ila"

import os
from django.urls import path
from main import users_v, config_v, schema_v, face_v
from dj2 import views

# from dj2.settings import dbName as schemaName

# url规则列表
urlpatterns = [
    path(r'users/register', users_v.users_register),
    path(r'users/login', users_v.users_login),
    path(r'users/logout', users_v.users_logout),
    path(r'users/session', users_v.users_session),
    path(r'users/page', users_v.users_page),
    path(r'users/save', users_v.users_save),
    path(r'users/info/<id_>', users_v.users_info),
    path(r'users/update', users_v.users_update),
    path(r'users/delete', users_v.users_delete),

    path(r'config/page', config_v.config_page),
    path(r'config/list', config_v.config_list),
    path(r'config/save', config_v.config_save),
    path(r'config/add', config_v.config_add),
    path(r'config/info/<id_>', config_v.config_info),
    path(r'config/detail/<id_>', config_v.config_detail),
    path(r'config/update', config_v.config_update),
    path(r'config/delete', config_v.config_delete),

]
# main app的路径
mainDir = os.path.join(os.getcwd(), "main")

# 过滤文件的列表
excludeList = [
    "schema_v.py",
    "users_v.py",
    "config_v.py",
    "face_v.py",
]

# 循环当前目录下的py文件

view_tuple = set()
for i in os.listdir(mainDir):
    if i not in excludeList and i[-5:] == "_v.py":
        viewName = i[:-3]  # 去掉.py后缀字符串
        view_tuple.add("from main import {}".format(viewName))

# 组合成import字符串
import_str = '\n'.join(view_tuple)
# print(import_str)
exec(import_str)

for i in os.listdir(mainDir):
    if i not in excludeList and i[-5:] == "_v.py":
        tableName = i[:-5]
        tableName = tableName.replace(" ", "").strip()
        print("tableName============>", tableName, len(tableName))

        urlpatterns.extend(
            [
                path(r'{}/register'.format(tableName.lower()),
                     eval("{}_v.{}_register".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/login'.format(tableName.lower()),
                     eval("{}_v.{}_login".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/logout'.format(tableName.lower()),
                     eval("{}_v.{}_logout".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/resetPass'.format(tableName.lower()),
                     eval("{}_v.{}_resetPass".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/session'.format(tableName.lower()),
                     eval("{}_v.{}_session".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/default'.format(tableName.lower()),
                     eval("{}_v.{}_default".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/page'.format(tableName.lower()),
                     eval("{}_v.{}_page".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/autoSort'.format(tableName.lower()),
                     eval("{}_v.{}_autoSort".format(tableName.capitalize(), tableName.lower()))),

                path(r'{}/save'.format(tableName.lower()),
                     eval("{}_v.{}_save".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/add'.format(tableName.lower()),
                     eval("{}_v.{}_add".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/thumbsup/<id_>'.format(tableName.lower()),
                     eval("{}_v.{}_thumbsup".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/info/<id_>'.format(tableName.lower()),
                     eval("{}_v.{}_info".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/detail/<id_>'.format(tableName.lower()),
                     eval("{}_v.{}_detail".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/update'.format(tableName.lower()),
                     eval("{}_v.{}_update".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/delete'.format(tableName.lower()),
                     eval("{}_v.{}_delete".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/vote/<id_>'.format(tableName.lower()),
                     eval("{}_v.{}_vote".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/importExcel'.format(tableName.lower()),
                     eval("{}_v.{}_importExcel".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/sendemail'.format(tableName.lower()),
                     eval("{}_v.{}_sendemail".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/autoSort2'.format(tableName.lower()),
                     eval("{}_v.{}_autoSort2".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/value/<xColumnName>/<yColumnName>/<timeStatType>'.format(tableName.lower()),
                     eval("{}_v.{}_value".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/value/<xColumnName>/<yColumnName>'.format(tableName.lower()),
                     eval("{}_v.{}_o_value".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/group/<columnName>'.format(tableName.lower()),
                     eval("{}_v.{}_group".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/valueMul/<xColumnName>/<timeStatType>'.format(tableName.lower()),
                     eval("{}_v.{}_valueMul".format(tableName.capitalize(), tableName.lower()))),
                path(r'{}/valueMul/<xColumnName>'.format(tableName.lower()),
                     eval("{}_v.{}_o_valueMul".format(tableName.capitalize(), tableName.lower()))),
            ]
        )
        #沙箱接口

        





        





        





        





        if tableName.lower() == "yonghu":
            urlpatterns.extend(
                [
                    path(r'{}/faceLogin'.format(tableName.lower()),
                         eval("{}_v.{}_faceLogin".format(tableName.capitalize(), tableName.lower())))
                ]
            )
        





        





        # examrecord特定接口
        if tableName.lower() == "examrecord":
            urlpatterns.extend(
                [
                    path(r'{}/groupby'.format(tableName.lower()),
                         eval("{}_v.{}_groupby".format(tableName.capitalize(), tableName.lower()))),
                    path(r'{}/deleteRecords'.format(tableName.lower()),
                         eval("{}_v.{}_deleterecords".format(tableName.capitalize(), tableName.lower()))),
                ]
            )

        # forum特定接口
        if tableName.lower() == "forum":
            urlpatterns.extend(
                [
                    path(r'{}/flist'.format(tableName.lower()),
                         eval("{}_v.{}_flist".format(tableName.capitalize(), tableName.lower()))),
                    path(r'{}/list/<id_>'.format(tableName.lower()),
                         eval("{}_v.{}_list_id".format(tableName.capitalize(), tableName.lower()))),
                    path(r'{}/list'.format(tableName.lower()),
                         eval("{}_v.{}_list".format(tableName.capitalize(), tableName.lower()))),
                ]
            )
        else:
            urlpatterns.extend(
                [
                    path(r'{}/list'.format(tableName.lower()),
                         eval("{}_v.{}_list".format(tableName.capitalize(), tableName.lower()))),
                ]
            )
urlpatterns.extend(
    [
        path(r'cal/<str:tableName>/<str:columnName>', schema_v.schemaName_cal),
        path(r'file/download', schema_v.schemaName_file_download),
        path(r'file/upload', schema_v.schemaName_file_upload),
        path(r'file/<path:filePath>', views.schema_file),
        path(r'follow/<tableName>/<columnName>/<level>/<parent>', schema_v.schemaName_follow_level),
        path(r'follow/<tableName>/<columnName>', schema_v.schemaName_follow),
        path(r'location', schema_v.schemaName_location),
        path(r'matchFace', schema_v.schemaName_matchface),
        path(r'option/<tableName>/<columnName>', schema_v.schemaName_option),
        path(r'remind/<tableName>/<columnName>/<type>', schema_v.schemaName_remind_tablename_columnname_type),
        # 前台提醒接口（通用接口，不需要登陆）
        path(r'<tableName>/remind/<columnName>/<type>', schema_v.schemaName_tablename_remind_columnname_type),
        # 后台提醒接口 (每个表的单独接口，需登录)
        path(r'sh/<tableName>', schema_v.schemaName_sh),
        path(r'group/<tableName>/<columnName>', schema_v.schemaName_group_quyu),
        path(r'value/<tableName>/<xColumnName>/<yColumnName>', schema_v.schemaName_value_quyu),
        path(r'value/<tableName>/<xColumnName>/<yColumnName>/<timeStatType>', schema_v.schemaName_value_riqitj),
        path(r'spider/<tableName>', schema_v.schemaName_spider),
    path(r'face/loginRecord', face_v.face_login_record),
    path(r'face/loginStats', face_v.face_login_stats),
    path(r'face/register', face_v.face_register_api),
    path(r'face/match', face_v.face_match_api),
    path(r'face/qualityCheck', face_v.face_quality_check),
    path(r'face/detectDemo', face_v.face_detect_demo),
    path(r'face/recognizeStranger', face_v.face_recognize_stranger),
    path(r'face/historyPage', face_v.face_history_page),
    path(r'face/regList', face_v.face_reg_list),
    path(r'face/deleteRecord', face_v.delete_login_record),
    path(r'face/batchDeleteRecords', face_v.batch_delete_records),
    path(r'face/strangerAlertList', face_v.stranger_alert_list),
    path(r'face/deleteStrangerRecord', face_v.delete_stranger_record),
    path(r'face/batchDeleteStrangerRecords', face_v.batch_delete_stranger_records),
    path(r'face/saveThreshold', face_v.save_threshold),
    path(r'system/config/get', face_v.system_config_get),
    path(r'system/config/set', face_v.system_config_set),
    path(r'dashboard/data', face_v.dashboard_data),
    path(r'user/changePassword', face_v.change_password),
    path(r'user/profile', face_v.user_profile_get),
    path(r'user/updateAvatar', face_v.update_user_avatar),
    path(r'user/updateProfile', face_v.update_user_profile),
    path(r'face/allAccounts', face_v.all_registered_accounts),
    path(r'face/updateAccountName', face_v.update_account_name),
    path(r'face/deleteAccount', face_v.delete_account),
    path(r'face/batchDeleteAccounts', face_v.batch_delete_accounts),
]
)

# print(urlpatterns)
