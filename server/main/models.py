#coding:utf-8
__author__ = "ila"
from django.db import models

from .model import BaseModel

from datetime import datetime



class syslog(BaseModel):
    __doc__ = u'''syslog'''
    __tablename__ = 'syslog'



    __authTables__={}
    __authPeople__='否'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    username=models.CharField ( max_length=50,null=False, unique=False, verbose_name='用户名' )
    operation=models.CharField ( max_length=100,null=False, unique=False, verbose_name='用户操作' )
    method=models.CharField ( max_length=10, null=True, unique=False, verbose_name='请求方法' )
    params=models.TextField   (  null=True, unique=False, verbose_name='请求参数' )
    time=models.BigIntegerField  (  null=True, unique=False, verbose_name='请求时长(毫秒)' )
    ip=models.CharField ( max_length=45, null=True, unique=False, verbose_name='ip地址' )
    '''
    username=VARCHAR
    operation=VARCHAR
    method=VARCHAR
    params=Text
    time=BigInteger
    ip=VARCHAR
    '''
    class Meta:
        db_table = 'syslog'
        verbose_name = verbose_name_plural = '操作日志'
class yonghu(BaseModel):
    __doc__ = u'''yonghu'''
    __tablename__ = 'yonghu'

    __loginUser__='yonghuzhanghao'


    __authTables__={}
    __authPeople__='是'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __loginUserColumn__='yonghuzhanghao'#用户表，表属性loginUserColumn对应的值就是用户名字段，mima就是密码字段
    __sfsh__='否'#表sfsh(是否审核，”是”或”否”)字段和sfhf(审核回复)字段，后台列表(page)的操作中要多一个”审核”按钮，点击”审核”弹出一个页面，包含”是否审核”和”审核回复”，点击确定调用update接口，修改sfsh和sfhf两个字段。
    __authSeparate__='否'#后台列表权限
    __thumbsUp__='否'#表属性thumbsUp[是/否]，新增thumbsupnum赞和crazilynum踩字段
    __intelRecom__='否'#智能推荐功能(表属性：[intelRecom（是/否）],新增clicktime[前端不显示该字段]字段（调用info/detail接口的时候更新），按clicktime排序查询)
    __browseClick__='否'#表属性[browseClick:是/否]，点击字段（clicknum），调用info/detail接口的时候后端自动+1）、投票功能（表属性[vote:是/否]，投票字段（votenum）,调用vote接口后端votenum+1
    __foreEndListAuth__='否'#前台列表权限foreEndListAuth[是/否]；当foreEndListAuth=是，刷的表新增用户字段userid，前台list列表接口仅能查看自己的记录和add接口后台赋值userid的值
    __foreEndList__='否'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    __isAdmin__='否'#表属性isAdmin=”是”,刷出来的用户表也是管理员，即page和list可以查看所有人的考试记录(同时应用于其他表)
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    yonghuzhanghao=models.CharField ( max_length=50,null=False,unique=True, verbose_name='用户账号' )
    mima=models.CharField ( max_length=255,null=False, unique=False, verbose_name='密码' )
    yonghuxingming=models.CharField ( max_length=32,null=False, unique=False, verbose_name='用户姓名' )
    touxiang=models.TextField   (  null=True, unique=False, verbose_name='头像' )
    lianxidianhua=models.CharField ( max_length=15, null=True, unique=False, verbose_name='联系电话' )
    xingbie=models.CharField ( max_length=2, null=True, unique=False, verbose_name='性别' )
    faceregistered=models.IntegerField(default=0, verbose_name='是否已注册人脸(0否1是)')
    mustchangepwd=models.IntegerField(default=0, verbose_name='是否需强制改密(0否1是)')
    facecount=models.IntegerField(default=0, verbose_name='已注册人脸数量')
    '''
    yonghuzhanghao=VARCHAR
    mima=VARCHAR
    yonghuxingming=VARCHAR
    touxiang=Text
    lianxidianhua=VARCHAR
    xingbie=VARCHAR
    faceregistered=Integer
    mustchangepwd=Integer
    facecount=Integer
    '''
    class Meta:
        db_table = 'yonghu'
        verbose_name = verbose_name_plural = '用户'
class menu(BaseModel):
    __doc__ = u'''menu'''
    __tablename__ = 'menu'



    __authTables__={}
    __foreEndList__='是'#表属性[foreEndList]前台list:和后台默认的list列表页相似,只是摆在前台,否:指没有此页,是:表示有此页(不需要登陆即可查看),前要登:表示有此页且需要登陆后才能查看
    addtime = models.DateTimeField(auto_now_add=False, verbose_name=u'创建时间')
    menujson=models.TextField   (  null=True, unique=False, verbose_name='菜单' )
    '''
    menujson=Text
    '''
    class Meta:
        db_table = 'menu'
        verbose_name = verbose_name_plural = '菜单'

class loginrecord(BaseModel):
    __doc__ = u'''loginrecord'''
    __tablename__ = 'loginrecord'
    __isAdmin__='是'
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'登录时间')
    username=models.CharField(max_length=50, verbose_name='用户名')
    role=models.CharField(max_length=20, default='用户', verbose_name='角色(管理员/用户/游客)')
    logintype=models.CharField(max_length=10, default='密码', verbose_name='登录方式(密码/人脸)')
    userid=models.BigIntegerField(null=True, verbose_name='用户ID(游客为空)')
    score=models.FloatField(null=True, verbose_name='人脸匹配分数')
    ipaddress=models.CharField(max_length=45, null=True, verbose_name='IP地址')
    useragent=models.TextField(null=True, verbose_name='浏览器信息')
    result=models.CharField(max_length=10, default='成功', verbose_name='结果(成功/失败)')
    faceimage=models.TextField(null=True, verbose_name='人脸截图路径(游客登录时保存)')
    isstranger=models.IntegerField(default=0, verbose_name='是否陌生人(0否1是)')
    class Meta:
        db_table = 'loginrecord'
        verbose_name = verbose_name_plural = '登录记录'

class faceregister(BaseModel):
    __doc__ = u'''faceregister'''
    __tablename__ = 'faceregister'
    __isAdmin__='是'
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'注册时间')
    userid=models.BigIntegerField(verbose_name='用户ID')
    username=models.CharField(max_length=50, verbose_name='用户名')
    faceimage=models.TextField(verbose_name='人脸图片路径')
    qualityscore=models.FloatField(default=0, verbose_name='图片质量分(0-100)')
    isvalid=models.IntegerField(default=1, verbose_name='是否有效(0无效1有效)')
    class Meta:
        db_table = 'faceregister'
        verbose_name = verbose_name_plural = '人脸注册记录'

class systemconfig(BaseModel):
    __doc__ = u'''systemconfig'''
    __tablename__ = 'systemconfig'
    addtime = models.DateTimeField(auto_now_add=True, verbose_name=u'更新时间')
    configkey=models.CharField(max_length=100, unique=True, verbose_name='配置键')
    configvalue=models.TextField(verbose_name='配置值')
    description=models.CharField(max_length=200, null=True, verbose_name='说明')
    class Meta:
        db_table = 'systemconfig'
        verbose_name = verbose_name_plural = '系统配置'
