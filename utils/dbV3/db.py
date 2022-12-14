# -*- coding: utf-8 -*-
# @Time    : 2022-01-15 15:32
# @Author  : 十七
# @Email   : 2429120006@qq.com
# @File    : db.py
# @Software: PyCharm
import ast
import re
import time
from configparser import ConfigParser
import pymysql
from DBUtils.PooledDB import PooledDB
from api.path import DB_CONFIG_PATH
from utils.crypto._MD5 import SM4Utils
import random
from utils.log.log import Logger
from utils.redisCache.redisCache import Redis

_redis = Redis()
log = Logger()


def getTodayTime():
    a = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return a


def random_id():
    a = ""
    for j in range(6):
        a += str((random.randint(0, 9)))
    return a


def returnJson(result=None, status=200, msg='操作成功'):
    """
    作为字典的形式返回数据响应
    @param result: 返回结果
    @param status: 返回状态码
    @param msg: 提示信息
    @return:
    """
    if result is None:
        return {'status': status, 'msg': msg}
    else:
        return {'status': status, 'msg': msg, 'result': result}


def handleLeaveContent(data):
    ...


def handleReturn(_res, data):
    """
    处理最终返回的结果
    @param _res:
    @param data:
    @return:
    """
    newData = data.get('result')
    _res.update(lt=newData)
    data.update(result=_res)
    return data


def handleTotal(data: dict) -> dict:
    """
    处理数据总数
    @param data:
    @return:
    """
    _res = {}
    total = data.get('result').get('total')
    _res.update(total=total)
    return _res


class database:
    def __init__(self):
        self.DbConnect_Pool = self.db_init()
        self.SM4 = SM4Utils()

    # def insert_ls_base(self, params):
    #     """
    #     暂存新增身高、体重、心率、体温
    #     先查询该体检条码是否存在，如果存在就更新，否则添加
    #     @param params:
    #     @return:
    #     """
    #     sql = f"""
    #             SELECT pc.RequisitionId  FROM pat_test_checklist pc WHERE pc.RequisitionId='{params.RequisitionId}'
    #         """
    def delete_card_by_userId(self, userId, cardId):
        """
        删除绑卡
        @param userId:
        @param cardId:
        @return:
        """
        sql = f"""
             UPDATE fh_personbasics SET cardId='{""}' WHERE userId={userId}
         """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def add_card_by_userId(self, userId, cardId):
        """
        添加用户卡号
        @param userId:
        @param cardId:
        @return:
        """
        # 先查询是否注册
        sql = f"""
            SELECT fp.cardId  FROM fh_personbasics fp WHERE fp.cardId='{cardId}'
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 13204:
            sql = f"""
                UPDATE fh_personbasics SET cardId='{cardId}' WHERE userId={userId}
            """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        elif res.get('status') == 200:
            res.update(status=13203, msg='该卡已被注册!')
        return res

    def get_upload_list(self, limit, page):
        """
        公卫获取上传体检列表
        @param limit:
        @param page:
        @return:
        """
        sql = """
        
                SELECT COUNT(*)`total` FROM pat_test_checklist ptc 
                LEFT JOIN fh_personbasics fp ON fp.userId=ptc.userId 
                LEFT JOIN sys_org so ON ptc.org_code=so.org_code 
                WHERE ptc.uploadStatus=1
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = handleTotal(res)
            sql = f"""
                            SELECT ptc.*,fp.`name`,fp.idCard,fp.gender,fp.birthday,
                            fp.nation,fp.phone,fp.cur_address,so.org_name 
                            FROM pat_test_checklist ptc 
                            LEFT JOIN fh_personbasics fp 
                            ON fp.userId=ptc.userId 
                            LEFT JOIN sys_org so 
                            ON ptc.org_code=so.org_code 
                            WHERE ptc.uploadStatus=1 LIMIT {(page - 1) * limit},{limit}
                
                """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
        return res

    def get_exam_echarts(self):
        """
        获取体检量化数据
        @return:
        """
        lt = []
        _res = {}
        result = {}
        total0 = 0
        total1 = 0
        sql0 = """
            SELECT COUNT(*)`total` FROM physical_type WHERE `status`=0
        """
        sql1 = """
            SELECT COUNT(*)`total` FROM physical_type WHERE `status`=1
        """
        res0 = self.SqlSelectByOneOrList(sql=sql0)
        res1 = self.SqlSelectByOneOrList(sql=sql1)
        if res0.get('status') == 200:
            d = {}
            total0 = res0.get('result', {}).get('total', 0)
            d.update(value=total0, name='待体检')
            lt.append(d)
        if res1.get('status') == 200:
            d = {}
            total1 = res1.get('result', {}).get('total', 0)
            d.update(value=total1, name='已完成')
            lt.append(d)
        result.update(pie=lt)
        total = total0 + total1
        if total != 0:
            percentage = round(total1 / (total0 + total1), 2)
        else:
            percentage = 0
        a = [{'value': percentage * 100}]
        result.update(dash=a)
        _res.update(status=200, msg='获取成功', result=result)
        return _res

    def get_org_code_echarts(self):
        """
        获取可视化数据
        @return:
        """
        d = {}
        res = {'status': 200, 'msg': '获取成功'}

        def status60():
            lt = []
            sql1 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060001' AND `status`=60
                   """
            res1 = self.SqlSelectByOneOrList(sql=sql1)
            sql2 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060002' AND `status`=60
                   """
            res2 = self.SqlSelectByOneOrList(sql=sql2)
            sql3 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060003' AND `status`=60
                   """
            res3 = self.SqlSelectByOneOrList(sql=sql3)
            sql4 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060004' AND `status`=60
                   """
            res4 = self.SqlSelectByOneOrList(sql=sql4)
            sql5 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060005' AND `status`=60
                   """
            res5 = self.SqlSelectByOneOrList(sql=sql5)
            sql6 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060006' AND `status`=60
                   """
            res6 = self.SqlSelectByOneOrList(sql=sql6)
            if res1.get('status') == 200:
                total = res1.get('result', {}).get('total', 0)
                lt.append(total)
            if res2.get('status') == 200:
                total = res2.get('result', {}).get('total', 0)
                lt.append(total)
            if res3.get('status') == 200:
                total = res3.get('result', {}).get('total', 0)
                lt.append(total)
            if res4.get('status') == 200:
                total = res4.get('result', {}).get('total', 0)
                lt.append(total)
            if res5.get('status') == 200:
                total = res5.get('result', {}).get('total', 0)
                lt.append(total)
            if res6.get('status') == 200:
                total = res6.get('result', {}).get('total', 0)
                lt.append(total)
            return lt

        def status20():
            lt = []
            sql1 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060001' AND `status`=20
                   """
            res1 = self.SqlSelectByOneOrList(sql=sql1)
            sql2 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060002' AND `status`=20
                   """
            res2 = self.SqlSelectByOneOrList(sql=sql2)
            sql3 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060003' AND `status`=20
                   """
            res3 = self.SqlSelectByOneOrList(sql=sql3)
            sql4 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060004' AND `status`=20
                   """
            res4 = self.SqlSelectByOneOrList(sql=sql4)
            sql5 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060005' AND `status`=20
                   """
            res5 = self.SqlSelectByOneOrList(sql=sql5)
            sql6 = """
                       SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060006' AND `status`=20
                   """
            res6 = self.SqlSelectByOneOrList(sql=sql6)
            if res1.get('status') == 200:
                total = res1.get('result', {}).get('total', 0)
                lt.append(total)
            if res2.get('status') == 200:
                total = res2.get('result', {}).get('total', 0)
                lt.append(total)
            if res3.get('status') == 200:
                total = res3.get('result', {}).get('total', 0)
                lt.append(total)
            if res4.get('status') == 200:
                total = res4.get('result', {}).get('total', 0)
                lt.append(total)
            if res5.get('status') == 200:
                total = res5.get('result', {}).get('total', 0)
                lt.append(total)
            if res6.get('status') == 200:
                total = res6.get('result', {}).get('total', 0)
                lt.append(total)
            return lt

        def status0():
            lt = []
            sql1 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060001' AND `status`=0
            """
            res1 = self.SqlSelectByOneOrList(sql=sql1)
            sql2 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060002' AND `status`=0
            """
            res2 = self.SqlSelectByOneOrList(sql=sql2)
            sql3 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060003' AND `status`=0
            """
            res3 = self.SqlSelectByOneOrList(sql=sql3)
            sql4 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060004' AND `status`=0
            """
            res4 = self.SqlSelectByOneOrList(sql=sql4)
            sql5 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060005' AND `status`=0
            """
            res5 = self.SqlSelectByOneOrList(sql=sql5)
            sql6 = """
                SELECT COUNT(*) `total` FROM fh_personbasics WHERE org_code='45060006' AND `status`=0
            """
            res6 = self.SqlSelectByOneOrList(sql=sql6)
            if res1.get('status') == 200:
                total = res1.get('result', {}).get('total', 0)
                lt.append(total)
            if res2.get('status') == 200:
                total = res2.get('result', {}).get('total', 0)
                lt.append(total)
            if res3.get('status') == 200:
                total = res3.get('result', {}).get('total', 0)
                lt.append(total)
            if res4.get('status') == 200:
                total = res4.get('result', {}).get('total', 0)
                lt.append(total)
            if res5.get('status') == 200:
                total = res5.get('result', {}).get('total', 0)
                lt.append(total)
            if res6.get('status') == 200:
                total = res6.get('result', {}).get('total', 0)
                lt.append(total)
            return lt

        d.update(status0=status0(), status20=status20(), status60=status0())
        res.update(result=d)
        return res

    def get_apply_data_total(self):
        resD = {}
        d = {'total': 0, 'unAuditTotal': 0, 'AuditTotal': 0,
             'rejectAuditTotal': 0}
        sql = """
                SELECT COUNT(*)`total` FROM physical.apply_table at 
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(total=res.get('result', {}).get('total', 0))
        sql = """
                SELECT COUNT(*)`unAuditTotal` FROM physical.apply_table at WHERE at.apply_status='0'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(unAuditTotal=res.get('result', {}).get('unAuditTotal', 0))
        sql = """
                    SELECT COUNT(*)`AuditTotal` FROM physical.apply_table at WHERE at.apply_status='1'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(AuditTotal=res.get('result', {}).get('AuditTotal', 0))
        sql = """
                    SELECT COUNT(*)`rejectAuditTotal` FROM physical.apply_table at WHERE at.apply_status='-1'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(rejectAuditTotal=res.get('result', {}).get('rejectAuditTotal', 0))

        resD.update(status=200, msg='获取成功', result=d)
        return resD

    def get_exam_type_by_cardId(self, cardId):
        """
        根据用户卡进行获取体检编码
        @param cardId:
        @return:
        """
        sql = f"""
               SELECT pt.RequisitionId FROM (SELECT * FROM fh_personbasics fp WHERE fp.cardId='{cardId}') a 
               JOIN physical_type pt ON pt.userId=a.userId 
               AND pt.status=0 ORDER BY pt.id DESC LIMIT 1
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def get_exam_data_total(self):
        """
        @return:
        """
        resD = {}
        d = {'total': 0, 'unAuditTotal': 0, 'AuditTotal': 0,
             'rejectAuditTotal': 0, 'unUploadTotal': 0, 'rejectUploadTotal': 0, 'UploadTotal': 0}
        sql = """
        SELECT COUNT(*)`total` FROM physical.pat_test_checklist ptc 
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(total=res.get('result', {}).get('total', 0))
        sql = """
        SELECT COUNT(*)`unAuditTotal` FROM physical.pat_test_checklist ptc WHERE ptc.auditStatus=0
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(unAuditTotal=res.get('result', {}).get('unAuditTotal', 0))
        sql = """
            SELECT COUNT(*)`AuditTotal` FROM physical.pat_test_checklist ptc WHERE ptc.auditStatus=1
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(AuditTotal=res.get('result', {}).get('AuditTotal', 0))
        sql = """
            SELECT COUNT(*)`rejectAuditTotal` FROM physical.pat_test_checklist ptc WHERE ptc.auditStatus=-1
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(rejectAuditTotal=res.get('result', {}).get('rejectAuditTotal', 0))
        sql = """
            SELECT COUNT(*)`unUploadTotal` FROM physical.pat_test_checklist ptc WHERE ptc.uploadStatus=0
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(unUploadTotal=res.get('result', {}).get('unUploadTotal', 0))
        sql = """
            SELECT COUNT(*)`UploadTotal` FROM physical.pat_test_checklist ptc WHERE ptc.uploadStatus=1
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(UploadTotal=res.get('result', {}).get('UploadTotal', 0))
        sql = """
            SELECT COUNT(*)`rejectUploadTotal` FROM physical.pat_test_checklist ptc WHERE ptc.uploadStatus=-1
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            d.update(rejectUploadTotal=res.get('result', {}).get('rejectUploadTotal', 0))
        resD.update(status=200, msg='获取成功', result=d)
        return resD

    def we_get_base_exam(self, rid):
        """
        根据rid查询基本体检结果
        @param rid:
        @return:
        """
        sql = f"""
                SELECT
                    ptc.Height,ptc.Weight,ptc.heart_rate,ptc.BMI,ptc.Temperature
                FROM
                    pat_test_checklist ptc
                    LEFT JOIN fh_personbasics fp ON ptc.userId = fp.userId
                    LEFT JOIN sys_org so ON ptc.org_code = so.org_code 
                WHERE
                    ptc.RequisitionId ='{rid}'
        """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            lt = []
            data = res.get('result', 0)
            for index, key in enumerate(data):
                d = {}
                if key == 'Height':
                    d.update(title='身高',
                             value=data.get('Height', '-'),
                             init='cm', scope='-')
                elif key == 'Weight':
                    d.update(title='体重',
                             value=data.get('Weight', '-'),
                             init='kg', scope='-')
                elif key == 'heart_rate':
                    d.update(title='心率/脉率',
                             value=data.get('heart_rate', '-'),
                             init='次/分', scope='60-100')
                elif key == 'BMI':
                    d.update(title='BMI',
                             value=data.get('BMI', '-'),
                             init='kg/m^2', scope='18.5-23.9')
                elif key == 'Temperature':
                    d.update(title='体温',
                             value=data.get('Temperature', '-'),
                             init='℃', scope='36.0-37.3')
                lt.append(d)
            res.update(result=lt)

        return res

    def we_get_exam_list(self, userId):
        """
        根据用户id查询体检列表
        @param userId:
        @return:
        """
        sql = f"""
                SELECT
                    ptc.*,
                    fp.`name`,
                    so.org_name 
                FROM
                    pat_test_checklist ptc
                    LEFT JOIN fh_personbasics fp ON ptc.userId = fp.userId
                    LEFT JOIN sys_org so ON ptc.org_code = so.org_code 
                WHERE
                    ptc.userId ={userId}
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def get_care(self, userId, rid):
        """
        查询自理评估
        @param userId:
        @param rid:
        @return:
        """
        sql = f"""
            SELECT fsca.*,su.sys_user_name
            FROM fh_self_care_assess fsca 
            LEFT JOIN sys_user su on fsca.doc_code = su.user_id  
            LEFT JOIN sys_org so on fsca.org_code = so.org_code
            WHERE RequisitionId='{rid}'
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def add_or_update_care(self, params: dict):
        """
        新增或更新自理评估
        @param params:
        @return:
        """
        sql = f"""
                    SELECT fsca.RequisitionId   FROM fh_self_care_assess fsca 
                    WHERE fsca.RequisitionId='{params.get("RequisitionId", 0)}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 13204:
            sql = f"""
            INSERT INTO fh_self_care_assess (
            userId, care_assess_status, org_code, doc_code, 
            care_assess_date, qus_id_1, qus_id_2, qus_id_3, qus_id_4, qus_id_5,
            final_point, remark, care_assess_level,
            modify_id, modify_time, RequisitionId
             ) VALUES (
             {params.get("userId")},1,'{params.get("org_code")}',{params.get("doc_code")},
             NOW(),'{params.get("qus_id_1")}','{params.get("qus_id_2")}','{params.get("qus_id_3")}',
             '{params.get("qus_id_4")}','{params.get("qus_id_5")}',
             '{params.get("final_point")}','{params.get("remark", "-")}',
            '{params.get("care_assess_level")}',
             {params.get("doc_code")},NOW(),'{params.get("RequisitionId")}'
             )
                    """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        elif res.get('status') == 200:
            sql = f"""
            UPDATE  fh_self_care_assess SET 
            care_assess_status=2,
            qus_id_1='{params.get("qus_id_1")}', qus_id_2='{params.get("qus_id_2")}', 
            qus_id_3='{params.get("qus_id_3")}', qus_id_4='{params.get("qus_id_4")}', 
            qus_id_5='{params.get("qus_id_5")}',
            final_point='{params.get("final_point")}', remark='{params.get("remark", "-")}', 
            care_assess_level='{params.get("care_assess_level")}',
            modify_id='{params.get("doc_code")}', modify_time=NOW() 
            WHERE RequisitionId='{params.get("RequisitionId", 0)}'
            """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        return res

    def get_depression(self, userId, rid):
        """
        查询抑郁评估
        @param userId:
        @param rid:
        @return:
        """
        sql = f"""
            SELECT * FROM fh_depression_assesss WHERE RequisitionId='{rid}'
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def add_or_update_depression(self, params: dict):
        """
        新增或更新抑郁评估
        @param params:
        @return:
        """
        sql = f"""
                    SELECT fda.RequisitionId   FROM fh_depression_assesss fda 
                    WHERE fda.RequisitionId='{params.get("RequisitionId", 0)}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 13204:
            sql = f"""
            INSERT INTO fh_depression_assesss (
            userId, depression_assesss_status, org_code, doc_code, 
            depression_assesss_date, qus_id_1, qus_id_2, qus_id_3, qus_id_4, qus_id_5,
            qus_id_6, qus_id_7, qus_id_8, qus_id_9, qus_id_10, qus_id_11, qus_id_12, 
            qus_id_13, qus_id_14, qus_id_15, qus_id_16, qus_id_17, qus_id_18, qus_id_19,
            qus_id_20, qus_id_21, qus_id_22, qus_id_23, qus_id_24, qus_id_25, qus_id_26, 
            qus_id_27, qus_id_28, qus_id_29, qus_id_30, final_point, remark, depression_assesss_level,
            modify_id, modify_time, RequisitionId
             ) VALUES (
             {params.get("userId")},1,'{params.get("org_code")}',{params.get("doc_code")},
             NOW(),'{params.get("qus_id_1")}','{params.get("qus_id_2")}','{params.get("qus_id_3")}',
             '{params.get("qus_id_4")}','{params.get("qus_id_5")}','{params.get("qus_id_6")}',
             '{params.get("qus_id_7")}','{params.get("qus_id_8")}','{params.get("qus_id_9")}',
             '{params.get("qus_id_10")}','{params.get("qus_id_11")}','{params.get("qus_id_12")}',
             '{params.get("qus_id_13")}','{params.get("qus_id_14")}','{params.get("qus_id_15")}',
             '{params.get("qus_id_16")}','{params.get("qus_id_17")}','{params.get("qus_id_18")}',
             '{params.get("qus_id_19")}','{params.get("qus_id_20")}','{params.get("qus_id_21")}',
             '{params.get("qus_id_22")}','{params.get("qus_id_23")}','{params.get("qus_id_24")}',
             '{params.get("qus_id_25")}','{params.get("qus_id_26")}','{params.get("qus_id_27")}',
             '{params.get("qus_id_28")}','{params.get("qus_id_29")}','{params.get("qus_id_30")}',
             '{params.get("final_point")}','{params.get("remark", "-")}',
            '{params.get("depression_assesss_level")}',
             {params.get("doc_code")},NOW(),'{params.get("RequisitionId")}'
             )
                    """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        elif res.get('status') == 200:
            sql = f"""
            UPDATE  fh_depression_assesss SET 
            depression_assesss_status=2,
            qus_id_1='{params.get("qus_id_1")}', qus_id_2='{params.get("qus_id_2")}', 
            qus_id_3='{params.get("qus_id_3")}', qus_id_4='{params.get("qus_id_4")}', 
            qus_id_5='{params.get("qus_id_5")}',
            qus_id_6='{params.get("qus_id_6")}', 
            qus_id_7='{params.get("qus_id_7")}', qus_id_8='{params.get("qus_id_8")}', 
            qus_id_9='{params.get("qus_id_9")}', qus_id_10='{params.get("qus_id_10")}', 
            qus_id_11='{params.get("qus_id_11")}', qus_id_12='{params.get("qus_id_12")}', 
            qus_id_13='{params.get("qus_id_3")}', qus_id_14='{params.get("qus_id_14")}', 
            qus_id_15='{params.get("qus_id_15")}',
             qus_id_16='{params.get("qus_id_16")}', qus_id_17='{params.get("qus_id_17")}', 
            qus_id_18='{params.get("qus_id_18")}', qus_id_19='{params.get("qus_id_19")}',
            qus_id_20='{params.get("qus_id_20")}', qus_id_21='{params.get("qus_id_21")}',
            qus_id_22='{params.get("qus_id_22")}', 
            qus_id_23='{params.get("qus_id_23")}', qus_id_24='{params.get("qus_id_24")}', 
            qus_id_25='{params.get("qus_id_25")}', qus_id_26='{params.get("qus_id_26")}', 
            qus_id_27='{params.get("qus_id_27")}', qus_id_28='{params.get("qus_id_28")}', 
            qus_id_29='{params.get("qus_id_29")}', 
            qus_id_30='{params.get("qus_id_30")}', 
            final_point='{params.get("final_point")}', remark='{params.get("remark", "-")}', 
            depression_assesss_level='{params.get("depression_assesss_level")}',
            modify_id='{params.get("doc_code")}', modify_time=NOW() 
            WHERE RequisitionId='{params.get("RequisitionId", 0)}'
            """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        return res

    def query_user_info(self, userId):
        """
        查询机构登录用户信息
        @param userId:
        @return:
        """
        sql = f"""
                SELECT su.*,so.org_name FROM physical.sys_user su 
                left join sys_org so on so.org_code=su.org_id 
                WHERE user_id={userId}
                """
        return self.SqlSelectByOneOrList(sql=sql)

    def pc_add_user(self, params):
        """
        添加用户
        @param params:
        @return:
        """
        sql = f"""
                    SELECT userId from fh_personbasics WHERE idCard='{params.get("idCard", 0)}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            sql = f""" 
                    UPDATE fh_personbasics 
                        SET `name`='{params.get("name", 0)}',idCard='{params.get("idCard", 0)}',
                                nation='{params.get("nation", 0)}',gender={params.get("gender", 0)},
                                org_code='{params.get("org_code", 0)}',
                                org_name= (SELECT org_name FROM sys_org WHERE org_code='{params.get("org_code", 0)}'),
                                cur_address='{params.get("cur_address")}',birthday='{params.get("birthday")}',
                                phone='{params.get("phone")}',
                                live_type={params.get("live_type", 0)},
                                blood_type='{params.get("blood_type", 0)}',`status`='{params.get("status", 0)}',
                                last_updator={params.get("last_updator", 0)},
                                last_updatime=NOW()
                        WHERE idCard = '{params.get("idCard", 0)}'
                    """
            res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        elif res.get('status') == 13204:
            sql = f""" 
                    SELECT userId from fh_personbasics ORDER BY userId DESC LIMIT 1
                """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 200:
                userId = res.get('result', {}).get('userId', 0)
                userId = int(userId) + 1
                sql = f""" 
                        INSERT INTO fh_personbasics 
                            (`name`,idCard,userId,nation,gender,
                            org_code,org_name,cur_address,birthday,
                            phone,live_type,blood_type,`status`,creator,creatime)
                            VALUES
                            ('{params.get("name", 0)}','{params.get("idCard")}',
                                {userId},'{params.get("nation")}',
                                {params.get("gender")},'{params.get("org_code")}',
                            (SELECT org_name FROM sys_org WHERE org_code='{params.get("org_code")}'),
                           '{params.get("cur_address")}','{params.get("birthday")}',
                            '{params.get("phone")}',{params.get("live_type")},
                            '{params.get("blood_type")}',{params.get("status")},
                            '{params.get("creator")}',NOW()
                            )
                            """
                res = self.insertOrUpdateOrDeleteBySql(sql=sql)

        return res

    def we_get_exam_result_by_rid_list(self, rid):
        """
        查询体检用户的生化体检结果
        @param rid:
        @return:
        """
        sql = f"""
                    SELECT FeeItemCode FROM pat_test_result WHERE RequisitionId='{rid}' GROUP BY FeeItemCode
                """
        res = self.SqlSelectByOneOrList(sql=sql, type=1)
        if res.get('status') == 200:
            arraylist = []
            for item in res.get('result', []):
                dictValueKey = {}
                sql = f"""
                           SELECT * FROM (SELECT ptr.*,zf.FeeItemName FROM pat_test_result ptr 
                            JOIN zd_feeitem zf ON ptr.FeeItemCode=zf.FeeItemCode 
                            WHERE ptr.RequisitionId='{rid}' AND ptr.FeeItemCode='{item.get("FeeItemCode", 0)}')
                            a GROUP BY a.ItemCode
                        """
                dictValueKey.update(sql=sql, key=item.get("FeeItemCode", 0))
                arraylist.append(dictValueKey)
            res = self.select_by_sqlList(sqlList=arraylist)
        return res

    def delete_user(self, userList: list):
        """
        批量删除用户
        @param userList:
        @return:
        """
        lt_sql = []
        for item in userList:
            sql = f"""
                        DELETE FROM physical.fh_personbasics WHERE idCard='{item.get("idCard", 0)}'
                    """
            lt_sql.append(sql)
        res = self.insertOrUpdateOrDeleteBySqlList(sqlList=lt_sql)
        return res

    def delete_sys_user(self, userList: list):
        """
        批量删除系统用户
        @param userList:
        @return:
        """
        lt_sql = []
        for item in userList:
            sql = f"""
                        DELETE FROM sys_user WHERE idCard='{item.get("idCard", 0)}'
                    """
            lt_sql.append(sql)
        res = self.insertOrUpdateOrDeleteBySqlList(sqlList=lt_sql)
        return res

    def update_sys_user(self, params: dict):
        """
        更新用户
        @param params:
        @return:
        """
        sql = f"""
                UPDATE sys_user SET  sys_user_account='{params.get("userAccount")}',
                            sys_user_password='{self.SM4.encryptData_ECB(plain_text=params.get("userPassword"))}',
                            sys_user_name='{params.get("userName")}',
                            phone='{params.get("phone")}',
                            org_id='{params.get("org_id")}',
                            status={params.get("status")},
                            sys_type={params.get("sys_type")},
                            account_change_time=NOW(),
                            authority={params.get("sys_type")},
                            sex={params.get("gender")},
                            birthday='{params.get("birthday")}'
                WHERE physical.sys_user.idCard='{params.get("idCard")}'
                """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def add_sys_user(self, params: dict):
        """
        新增系统用户
        @param params:
        @return:
        """
        sql = f"""
                SELECT * FROM sys_user su WHERE idCard='{params.get("idCard", 0)}'
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            res.update(msg='用户已存在', status=13206)
        elif res.get('status') == 13204:
            sql = f"""
                    SELECT user_id FROM sys_user ORDER BY user_id DESC 
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get("status") == 200:
                user_id = int(res.get('result').get('user_id')) + 1
                sql = f"""
                        INSERT INTO sys_user 
                        (
                            sys_user_account,
                            sys_user_password,
                            sys_user_name,
                            user_id,
                            phone,
                            idCard,
                            org_id,
                            status,
                            sys_type,
                            register_time,
                            create_by,
                            account_change_time,
                            authority,
                            sex,birthday
                        )VALUES (
                                '{params.get("userAccount")}',
                                '{self.SM4.encryptData_ECB(plain_text=params.get("userPassword"))}',
                            '{params.get("userName")}',
                            {user_id},
                            '{params.get("phone")}',
                            '{params.get("idCard")}',
                            '{params.get("org_id")}',
                            {params.get("status")},
                            {params.get("sys_type")},
                            NOW(),
                            '{params.get("create_by")}', 
                            NOW(),
                            {params.get("sys_type")},
                            {params.get("gender")},
                            '{params.get("birthday")}')
                        """
                res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        return res

    def query_sys_org_list(self):
        """
        查询系统机构列表
        @return:
        """
        sql = f"""
                SELECT * FROM sys_org
            """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def query_sys_user(self, page=1, limit=20):
        """
        查询系统用户
        @param page:
        @param limit:
        @return:
        """

        sql = f"""
                    SELECT COUNT(*) `total` FROM sys_user
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = handleTotal(res)
            sql = f"""
                        SELECT *  FROM sys_user 
                            ORDER BY id DESC  
                            limit {(page - 1) * limit},{limit}
                    """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
        return res

    def we_exam_list_by_userId(self, userId):
        """
        查询申请体检列表
        @param userId:
        @return:
        """
        sql = f"""
                SELECT pt.userId,pt.FeeItemCodeList,pt.RequisitionId,
                    pt.applyId,CONVERT(pt.creatTime,CHAR(10)) `creatTime` ,pt.status,fp.name
                    FROM physical_type pt
                    join fh_personbasics fp on pt.userId = fp.userId
                    WHERE pt.userId={userId} ORDER BY pt.creatTime DESC 
            """
        res = self.SqlSelectByOneOrList(sql=sql, type=1)
        return res

    def RegisterSql(self, pwd: str, nick: str, idCard: str) -> dict:  # 注册验证
        """
        注册函数
        :param pwd: 密码
        :param nick: 昵称
        :param idCard: 有效证件
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        idCardDe = self.SM4.decryptData_ECB(idCard)  # 身份证解密
        try:
            _queryIsExistByIdCard = f"""
               SELECT id,idCard,name from fh_personbasics where idCard='{idCardDe}'
               """
            _queryRes = self.SqlSelectByOneOrList(sql=_queryIsExistByIdCard)
            RESULT = _queryRes.get("result")
            if _queryRes.get('status') == 200:  # 查询身份证成功
                _queryIsRegistered = f"""
                    SELECT a.idCard from fh_personbasics a 
                    join userinfo b on a.id = b.relation where a.idCard='{idCardDe}'
                   """
                _queryIsRegisteredRes = self.SqlSelectByOneOrList(sql=_queryIsRegistered)
                if _queryIsRegisteredRes.get("status") == 200:  # 此时能查询到，说明已经注册过
                    res.update(status=13205, msg="已开通，无需重复")
                elif _queryIsRegisteredRes.get("status") == 13204:  # 此时没能查询到，说明未注册过，可以注册
                    if nick == '':
                        nick = RESULT.get('name')
                    account = RESULT.get('idCard')[-6:]
                    if account[0] in [0, '0']:
                        account[0] = '1'
                    _sqlInsertByRegister = """
                       INSERT INTO userinfo 
                       ( userAccount,name, relation,userPassword,nickName,status,authority) 
                       VALUES ('{}','{}','{}','{}','{}',1,0
                       )

                       """.format(account, RESULT.get('name'), RESULT.get('id'), pwd, nick)
                    _res = self.insertOrUpdateOrDeleteBySql(sql=_sqlInsertByRegister)
                    if _res.get('status') == 200:
                        res.update(status=_res.get('status'), msg="开通成功")
                    else:
                        res.update(status=_res.get('status'), msg=_res.get('msg'))
            elif _queryRes.get('status') == 13204:
                res.update(status=_queryRes.get('status'), msg="用户不存在")
            else:
                res.update(status=_queryRes.get('status'), msg="操作失败")
            return res
        except Exception as e:
            print(e)
            res.update(status=13203, msg=e)
            return res

    def query_user_details_by_idCard(self, idCard, org_code):
        """
        通过身份证查询本机构用户基本信息与体检项目类型
        @param idCard:
        @param org_code:
        @return:
        """
        res = self.user_details_by_idCard(idCard=idCard)
        print(res)
        if res.get("status") == 200:
            _res = self.select_feeItemCode_list()
            print(_res)
            if _res.get('status') == 200:
                res.get('result').update(codeList=_res.get('result'))
                print(res)
        return res

    def exam_result_upload_by_rid(self, rid, uploadStatus):
        """
        根据体检编码上传体检结果
        @param rid:
        @param uploadStatus:
        @return:
        """
        sql = f"""
                UPDATE pat_test_checklist SET uploadStatus={uploadStatus},uploadTime=NOW() WHERE RequisitionId='{rid}'
            """
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def exam_result_audit_by_rid(self, rid, status, remark):
        """
        医生审核体检结果
        @param rid: 体检编码
        @param status: 0-未审核，1-已审核，-1-不通过
        @param remark: 不通过原因
        @return:
        """
        if status in [-1, '-1']:
            sql = f"""
                        UPDATE  pat_test_checklist  SET auditStatus={status},Status=0,
                        remark='{remark if remark else ""} ',uploadStatus=0
                        WHERE RequisitionId='{rid}'
                """
        else:
            sql = f"""
                        UPDATE  pat_test_checklist  SET auditStatus={status},Status={status},uploadStatus=0
                        WHERE RequisitionId='{rid}'
                """
            sql2 = f"""
                           UPDATE  physical_type  SET status={status}
                           WHERE RequisitionId='{rid}'
                   """
            self.insertOrUpdateOrDeleteBySql(sql=sql2)
        return self.insertOrUpdateOrDeleteBySql(sql=sql)

    def query_exam_base_and_urine_by_rid(self, rid):
        """
        通过体检编码查询体检结果
        @param rid:
        @return:
        """
        sql = f"""
                SELECT PTC.RequisitionId,PTC.org_code `exam_org_code`,
            PTC.ProjectName,PTC.ProjectNo,PTC.RSBP,PTC.RDBP,
                    PTC.Height,PTC.Weight,PTC.BMI,PTC.Temperature,
                    PTC.Operator,CONVERT(PTC.VisitingDate,CHAR(19)) `VisitingDate`,PTC.Status,
                        PTC.ReviewDoctor,PTC.ReviewDate,PTC.LSBP,
                PTC.LDBP,PTC.heart_rate,PTC.uploadStatus,PTC.remark,PTC.auditStatus,
                        fp.birthday,fp.org_name,fp.org_name,fp.idCard,fp.cur_address,fp.phone,fp.idCard,
                        fp.gender,fp.name
                    FROM pat_test_checklist PTC join fh_personbasics fp on PTC.userId = fp.userId
                    WHERE PTC.RequisitionId='{rid}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            # 先查询分类
            sql = f"""
                select FeeItemCode from pat_test_result WHERE RequisitionId='{rid}' GROUP BY FeeItemCode
                    """
            _res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if _res.get('status') == 200:
                data = {}
                for index, item in enumerate(_res.get('result')):
                    FeeItemCode = item.get('FeeItemCode', 0)
                    RES = self.query_exam_base_and_urine_by_feeItemCode(FeeItemCode, rid)
                    a = {FeeItemCode: RES}
                    data.update(a)
                res.get('result').update(data)
            # 查询老年人相关
            # 自立评估
            sql_fsa = f"""
                SELECT fsa.* FROM fh_self_care_assess fsa WHERE fsa.RequisitionId='{rid}'       
            """
            # 智力评估
            sql_mse = f"""
                SELECT mse.* FROM fh_mental_state_exam mse WHERE mse.RequisitionId='{rid}'
            """
            # 抑郁评估
            sql_fda = f"""
               SELECT fda.* FROM fh_depression_assesss fda WHERE fda.RequisitionId='{rid}'
            """
            # 抑郁评估
            sql_ffz = f"""
              SELECT ffz.* FROM fh_follow_zyyjk ffz WHERE ffz.RequisitionId='{rid}'
            """
            old = {'self_care_assess': '', 'mental_state_exam': '',
                   'depression_assesss': '', 'follow_zyyjk': ''}
            fsaRes = self.SqlSelectByOneOrList(sql=sql_fsa)
            if fsaRes.get('status') == 200:
                old.update(self_care_assess=fsaRes.get('result', {}))
            mseRes = self.SqlSelectByOneOrList(sql=sql_mse)
            if mseRes.get('status') == 200:
                old.update(mental_state_exam=mseRes.get('result', {}))
            fdaRes = self.SqlSelectByOneOrList(sql=sql_fda)
            if fdaRes.get('status') == 200:
                old.update(depression_assesss=fdaRes.get('result', {}))
            ffzRes = self.SqlSelectByOneOrList(sql=sql_ffz)
            if ffzRes.get('status') == 200:
                old.update(follow_zyyjk=ffzRes.get('result', {}))
            res.get('result').update(old)
        return res

    def query_exam_base_and_urine_by_feeItemCode(self, FIC, rid):
        """
        通过项目编码大类和体检编码查询结果
        @param FIC:
        @param rid:
        @return:
        """
        sql = f"""
                SELECT  Did,
                    RequisitionId,
                    FeeItemCode,
                    ItemCode,
                    ItemName,
                    ReceivedTime,
                    Lis_RangeState,
                    Lis_Result,
                    Lis_ResultUnit,
                    Lis_ReferenceRange,
                    Lis_RangeLowValue,
                    Lis_RangeHighValue,
                    Lis_RangeStateColor
                    FROM pat_test_result WHERE FeeItemCode='{FIC}' AND RequisitionId='{rid}'
                """
        res = self.SqlSelectByOneOrList(sql=sql, type=1)
        if res.get("status") == 200:
            return res.get("result")
        else:
            return []

    def check_exam_type_btn_by_rid(self, rid):
        """
        根据体检编码校验是否前端可以生成数据，要与选择体检的项目一致
        @param rid:
        @return:
        """
        sql = f"""
                SELECT PT.FeeItemCodeList FROM physical_type PT WHERE PT.RequisitionId='{rid}' AND PT.status=0
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            result = ast.literal_eval(res.get('result').get('FeeItemCodeList'))
            result = dict(zip(result, result))
            res.update(result=result)
        return res

    def insert_exam_urine_by_rid(self, rid, params):
        """
        根据体检编码新增尿检结果
        @param rid:
        @param params:
        @return:
        """
        sqlList = []
        try:
            for index, item in enumerate(params):
                # 查询是否已经存在结果，如果存在，则更新
                sql = f"""
                    SELECT
                        ptr.ItemCode 
                    FROM
                        pat_test_result ptr 
                    WHERE
                        ptr.RequisitionId = '{rid}' 
                        AND ptr.ItemCode = '{item.get("ItemCode")}'
                        """
                checkRes = self.SqlSelectByOneOrList(sql=sql)
                if checkRes.get("status") == 13204:
                    sql = f"""
                            INSERT INTO pat_test_result (RequisitionId, FeeItemCode, ItemCode,
                                    ItemName, ReceivedTime, Lis_Result, Lis_ResultUnit,
                                    Lis_ReferenceRange
                                )VALUES ('{rid}','{item.get("FeeItemCode")}','{item.get("ItemCode")}',
                                  '{item.get("ItemName")}',NOW(),'{item.get("Lis_Result")}',
                                    '{item.get("Lis_ResultUnit", "-")}','{item.get("Lis_ReferenceRange")}')
                        """
                else:
                    sql = f"""
                            UPDATE pat_test_result 
                            SET Lis_Result = '{item.get("Lis_Result")}',
                            Lis_ResultUnit = '{item.get("Lis_ResultUnit", "-")}' 
                            WHERE
                                RequisitionId = '{rid}' 
                                AND ItemCode = '{item.get("ItemCode")}'
                           """
                sqlList.append(sql)
            res = self.insertOrUpdateOrDeleteBySqlList(sqlList=sqlList)
            return res
        except Exception as e:
            print(e)

    def query_exam_base_by_rid(self, rid):
        """
        通过体检编码查询基本体检结果
        @return:
        """
        sql = f"""  
            SELECT PC.*,fp.name,fp.idCard,fp.org_name,fp.birthday FROM  pat_test_checklist PC 
        join fh_personbasics fp on PC.userId = fp.userId WHERE PC.RequisitionId='{rid}'
                ORDER BY PC.Did DESC limit 1
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def query_exam_upload_by_org_code(self, org_code, page=1, limit=20):
        """
        根据机构编码查询体检上传
        @param org_code:
        @param page:
        @param limit:
        @return:
        """
        sql = f"""
            SELECT count(*) `total` FROM  pat_test_checklist PC 
            join fh_personbasics fp on PC.userId = fp.userId WHERE PC.org_code='{org_code}'
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = handleTotal(res)
            sql = f"""  
                SELECT PC.*,fp.name,fp.idCard,fp.org_name FROM  pat_test_checklist PC 
            join fh_personbasics fp on PC.userId = fp.userId WHERE PC.org_code='{org_code}'
                    ORDER BY PC.Did DESC 
                   limit {(page - 1) * limit},{limit}
                    """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
        return res

    def query_user_info_by_rid(self, rid):
        """
        通过RequisitionId查询用户
        @param rid: RequisitionId
        @return:
        """
        sql = f"""
                    SELECT PT.userId  FROM physical_type PT WHERE PT.RequisitionId='{rid}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            userId = res.get('result').get('userId')
            res = self.userDetailsByUserId(userId=userId)
            return res
        else:
            return res

    def insert_base_exam(self, params):
        """
        添加或更新一般体检信息，
        @param params:
        @return:
        """
        sql = f"""
                SELECT PTC.RequisitionId  FROM pat_test_checklist PTC WHERE PTC.RequisitionId='{params.get("RequisitionId")}'
                """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get("status") == 13204:
            sql = f"""
                    INSERT INTO pat_test_checklist (
                        RequisitionId, userId, org_code, 
                        ProjectNo,ProjectName, RSBP, RDBP,Height,
                        Weight, BMI, Temperature, Operator, VisitingDate, 
                        Status, LSBP, LDBP, heart_rate) VALUES 
                    ('{params.get("RequisitionId")}',{params.get("userId")},'{params.get("org_code")}'
                        ,30,'健康体检',70,90,{params.get("Height")},{params.get("Weight")},{params.get("BMI", 0)},{params.get("Temperature", 36.0)},
                        '{params.get("Operator")}','{params.get("VisitingDate")}',{0},{params.get("LSBP", 0)},{params.get("LDBP", 0)},
                            '{params.get("heart_rate", 0)}')
                """
        elif res.get("status") == 200:
            sql = f""" 
                    UPDATE pat_test_checklist SET RequisitionId='{params.get("RequisitionId", 0)}', userId='{params.get("userId")}',
                        org_code='{params.get("org_code")}', 
                        RSBP={params.get("RSBP", 0)}, RDBP={params.get("RDBP", 0)},Height={params.get("Height", 0)},
                        Weight={params.get("Weight", 0)}, BMI={params.get("BMI", 0)}, Temperature='{params.get("Temperature", 0)}',
                        Operator='{params.get("Operator")}', VisitingDate='{params.get("VisitingDate")}', 
                        LSBP={params.get("LSBP", 0)}, LDBP={params.get("LDBP", 0)}, heart_rate={params.get("heart_rate", 0)} 
                    WHERE RequisitionId='{params.get("RequisitionId", 0)}'
                    """
            print(sql)
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        return res

    def select_person_physical_list_by_RequisitionId(self, RequisitionId):
        """
        根据当次体检编码查询当前用户需要体检的项目大类
        @param RequisitionId:
        @return:
        """
        sql = f"""
                SELECT
                    pt.userId,
                    pt.FeeItemCodeList `examList`,
                    pt.applyId,
                    CONVERT (
                        pt.creatTime,
                    CHAR ( 19 )) `creatTime`,
                    pt.RequisitionId,
                    pt.id,
                    fp.name,fp.idCard,fp.gender,fp.birthday,fp.org_name,fp.org_code,fp.phone,fp.cur_address
                FROM
                    physical_type pt LEFT JOIN fh_personbasics fp on pt.userId = fp.userId
                WHERE
                    RequisitionId = '{RequisitionId}' ORDER BY pt.id DESC LIMIT 1
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            examListString = res.get('result').get('examList')
            userInfo = res.get('result')
            examListList = ast.literal_eval(examListString)
            examListTuple = tuple(examListList)
            sql = f"""
                 SELECT
                   DISTINCT F.FeeItemCode,F.FeeItemName 
                FROM
                    zd_feeitem F 
                WHERE
                    F.FeeItemCode IN (
                    SELECT
                        a.FeeItemCode 
                    FROM
                        ( SELECT DISTINCT FeeItemCode FROM zd_feeitem WHERE FeeItemCode IN {examListTuple} AND isUse = 1 ) a 
                    ) 
                    AND F.isUse =1
            """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get('status') == 200:
                result = res.get('result')
                new_res = []
                exam_list = {}
                exam_list.update(userInfo)
                for index, item in enumerate(result):
                    select_res = self.select_itemCode_list_by_feeItemCode(feeItemCode=item.get('FeeItemCode'))
                    if select_res.get('status') == 200:
                        _res = select_res.get('result')
                        new_res.append(_res)
                exam_list.update(list=new_res)
                res.update(result=exam_list)
            # examListRes = self.SqlSelectByOneOrList(sql=sql, type=1)
            # if examListRes.get('status') == 200:
            #     examListRes = examListRes.get('result')
            #     res.get('result').update(examList=examListRes)
        return res

    def update_apply_by_id(self, Id, apply_status, operator_id, apply_reason=None):
        """
        更新用户的申请状态
        @param Id: 对应的数据id
        @param apply_status:状态
        @param apply_reason:原因，拒绝时使用
        @param operator_id:操作人id
        @return:
        """
        if apply_status in [-1, '-1'] and apply_reason:
            sql = f"""
                    UPDATE apply_table 
                    SET apply_status = {apply_status},apply_reason='{apply_reason}',
                        operator_id={operator_id},complete_time=NOW()
                    WHERE
                        id ={Id}
                    """
        elif apply_status in [-1, '-1']:
            sql = f"""
                    UPDATE apply_table 
                    SET apply_status = {apply_status},
                        operator_id={operator_id},complete_time=NOW()
                    WHERE
                        id ={Id}
                    """
        elif apply_status in [0, '0']:
            sql = f"""
                      UPDATE apply_table 
                      SET apply_status = {apply_status} ,operator_id={operator_id}
                      ,complete_time=NULL,apply_reason=NULL
                      WHERE
                          id ={Id}
                      """
        else:
            sql = f"""
                    UPDATE apply_table 
                    SET apply_status = {apply_status} ,operator_id={operator_id}
                    ,complete_time=NOW(),apply_reason=NULL
                    WHERE
                        id ={Id}
                    """
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        if res.get('status') == 200:
            if apply_status in [1, '1']:
                addStatus = self.add_or_update_physical_type(Id=Id)
                if addStatus:
                    res.update(msg="操作成功")
                else:
                    res.update(status=13203, msg='操作异常')
            elif apply_status in [0, '0']:
                self.delete_physical_type(Id=Id)
        return res

    def delete_physical_type(self, Id):
        """
        删除记录
        @param Id: 对应表apply_type中的Id
        @return:
        """
        sql = f"""
                  DELETE FROM physical_type WHERE applyId={Id}
                
                """
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)

    def add_or_update_physical_type(self, Id):
        """
        新增[更新]表physical_type
        @param Id: 对应表apply_type中的Id
        @return:
        """
        # 获取RequisitionId
        RequisitionId = self.getLastRequisitionIdOrBarCode()
        if RequisitionId:
            sql = f"""
                   INSERT INTO physical_type(
                            userId,
                            FeeItemCodeList,
                            RequisitionId,
                            applyId,
                            creatTime,
                            status
                    )
                            SELECT
                                userId,
                                apply_type,
                                '{RequisitionId + 1}',
                                id,
                                NOW(),
                                0
                            FROM
                                apply_table
                            WHERE
                                id = {Id}
                    """
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        if res.get("status") == 200:
            # 更新RequisitionId
            res = self.updateLastRequisitionIdOrBarCode(updateValue=str(RequisitionId + 1))
            return res
        else:
            return False

    def select_itemCode_list_by_feeItemCode(self, feeItemCode):
        """
        根据feeItemCode查询所有子项
        @param feeItemCode:
        @return:
        """
        sql = f"""
            SELECT
                COUNT(*) `total`
            FROM
                (
                SELECT *
                FROM
                    zd_feeitem 
                WHERE
                isUse = 1 AND FeeItemCode='{feeItemCode}') a
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = handleTotal(res)
            sql = f"""
                    SELECT
                    FeeItemCode,
                    FeeItemName,
                    FormType,
                    ItemCode,ItemName
                FROM
                    zd_feeitem 
                WHERE
                    isUse =1 AND FeeItemCode='{feeItemCode}'
                """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                for index, item in enumerate(res.get('result')):
                    FeeItemCode = item.get('FeeItemCode')
                    item.pop('FeeItemCode', None)  # 删除
                    FeeItemName = item.get('FeeItemName')
                    item.pop('FeeItemName', None)
                    _res.update(FeeItemCode=FeeItemCode)
                    _res.update(FeeItemName=FeeItemName)
                res = handleReturn(_res, res)
        return res

    def select_feeItemCode_list(self):
        """
        查询体检项目大类
        @return:
        """
        sql = f"""
                SELECT
                    COUNT(*) `total`
                FROM
                    (
                    SELECT DISTINCT
                        FeeItemCode,
                        FeeItemName,
                        FormType 
                    FROM
                        zd_feeitem 
                    WHERE
                    isUse = 1) a
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = {}
            total = res.get('result').get('total')
            _res.update(total=total)
            sql = f"""
                SELECT DISTINCT
                    FeeItemCode,
                    FeeItemName,
                    FormType 
                FROM
                    zd_feeitem 
                WHERE
                    isUse =1
                """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            print(sql)
            if res.get("status") == 200:
                data = res.get('result')
                _res.update(lt=data)
                res.update(result=_res)
        return res

    def query_apply_by_text(self, searchText, page=1, limit=50):
        """
        搜索。支持姓名，机构名称，身份证
        @param searchText: 搜索内容
        @param page:
        @param limit:
        @return:
        """
        sql = f"""
             SELECT COUNT(*) `total`
             FROM
                 apply_table
                 AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
             WHERE
                 fp.name LIKE '%{searchText}%' OR fp.idCard LIKE '%{searchText}%' 
                OR fp.org_name LIKE '%{searchText}%' AND fp.status=0
             """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = {}
            total = res.get('result').get('total')
            _res.update(total=total)
            sql = f"""
                    SELECT AT
                      .id,AT.org_code,AT.apply_type,CONVERT(AT.apply_time,CHAR(19)) `apply_time`,
                            CONVERT(AT.complete_time,CHAR(19)) `complete_time`,AT.apply_status,
                            AT.apply_reason,AT.operator_id,AT.userId
                        ,fp.org_name,fp.idCard,fp.name,fp.gender,su.sys_user_name `operator_name`,
                            CONVERT(fp.birthday,CHAR(10)) `birthday`
                FROM
                    apply_table
                    AT LEFT JOIN fh_personbasics fp ON AT.userId = fp.userId LEFT join sys_user su on su.user_id = AT.operator_id
                  WHERE
                     fp.name LIKE '%{searchText}%' OR fp.idCard LIKE '%{searchText}%' 
                    OR fp.org_name LIKE '%{searchText}%' AND fp.status=0
                  ORDER BY
                     AT.apply_time desc limit {(page - 1) * limit},{limit}
                  """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get("status") == 200:
                data = res.get('result')
                data = self.handle_feeItemCode(data=data)
                _res.update(lt=data)
                res.update(result=_res)
                _redis.set(key=f"searchApply{searchText}{page}{limit}", value=str(res), timeout=60)
        return res

    def select_apply_by_org_code(self, org_code, page=1, limit=50):
        """
        通过机代码查询用户申请列表
        @param org_code: 机构代码
        @param page: 页
        @param limit: 大小
        @return:
        """
        sql = f"""
            SELECT COUNT(*) `total`
            FROM
                apply_table
                AT JOIN fh_personbasics fp ON AT.userId = fp.userId 
            WHERE
                AT.org_code = '{org_code}' AND fp.status=0
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = {}
            total = res.get('result').get('total')
            _res.update(total=total)
            sql = f"""
                  SELECT AT
                      .id,AT.org_code,AT.apply_type,CONVERT(AT.apply_time,CHAR(19)) `apply_time`,
                            CONVERT(AT.complete_time,CHAR(19)) `complete_time`,AT.apply_status,
                            AT.apply_reason,AT.operator_id,AT.userId
                        ,fp.org_name,fp.idCard,fp.name,fp.gender,
                            CONVERT(fp.birthday,CHAR(10)) `birthday`,su.sys_user_name `operator_name`
                FROM
                    apply_table
                    AT LEFT JOIN fh_personbasics fp ON AT.userId = fp.userId 
                    LEFT join sys_user su on su.user_id = AT.operator_id
                WHERE
                    AT.org_code = '{org_code}' AND fp.status=0
                ORDER BY
                   AT.apply_time desc limit {(page - 1) * limit},{limit}
                """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get('status') == 200:
                data = res.get('result')
                data = self.handle_feeItemCode(data=data)
                _res.update(lt=data)
                res.update(result=_res)
                # _redis.set(key=f"apply{org_code}{page}{limit}", value=str(res), timeout=60)
        return res

    def handle_feeItemCode(self, data):
        """
        根据传过来的feeItemCode编码列表，查询对应的名称与编码
        @param data:
        @return:
        """
        new_data = []
        sql_list = []
        try:
            for index, item in enumerate(data):
                # 每条数据
                feeItemCodeListString = item.get("apply_type")
                feeItemCodeList = ast.literal_eval(feeItemCodeListString)
                feeItemCodeTuple = tuple(feeItemCodeList)
                # if isinstance(data, list):  # 数据类型是否为列表
                if len(feeItemCodeTuple) > 1:
                    sql = f"""
                            SELECT DISTINCT zf.FeeItemCode,zf.FeeItemName FROM zd_feeitem zf 
                            WHERE zf.FeeItemCode IN 
                            {feeItemCodeTuple} 
                            AND zf.isUse=1
                        """
                else:
                    sql = f"""
                            SELECT DISTINCT zf.FeeItemCode,zf.FeeItemName FROM zd_feeitem zf 
                            WHERE zf.FeeItemCode IN ('{feeItemCodeTuple[0]}')
                            AND zf.isUse=1
                        """
                sql_list.append(sql)
            res = self.SqlListSelectByOneOrList(sqlList=sql_list, oldData=data)
            if res.get('status') == 200:
                res = res.get('result')
                # item.update(apply_type=new_apply_type)
                # new_data.append(item)
                return res
            else:
                return None
        except Exception as e:
            log.logger.error(str(e))

    def we_insert_apply_by_userId(self, userId, apply_type):
        """
        添加用户申请
        @param userId: 用户ID
        @param apply_type: 申请类型
        @return:
        """
        try:
            sql = f"""
                    SELECT fp.org_code  FROM fh_personbasics fp WHERE fp.userId={userId}
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get("status") == 200:
                org_code = res.get('result').get('org_code')
                sql = f"""
                        SELECT *  FROM apply_table WHERE apply_status=0 AND userId='{userId}'
                        """
                RES = self.SqlSelectByOneOrList(sql=sql)
                if RES.get('status') == 13204:
                    sql = f"""
                              INSERT INTO apply_table 
                                  (userId, apply_type, apply_time, apply_status, org_code)
                              VALUES ({userId},'{apply_type}',NOW(),0,'{org_code}')
                          """
                else:
                    sql = f"""
                              UPDATE  apply_table SET apply_type='{apply_type}' WHERE userId='{userId}'
                          """
                res = self.insertOrUpdateOrDeleteBySql(sql=sql)
            return res
        except Exception as e:
            print(e)

    def we_queryBasicPhysicalExamRes(self, Rid=None) -> dict:
        """
           根据体检条码查询基本体检详情
            身高、体重、体温、心率
        @param Rid: 查询基本体检数据
        @return:
        """
        sql = f"""
                SELECT 
                        pc.Height,pc.Weight,pc.BMI,
                        pc.RequisitionId,pc.LSBP,pc.LDBP,pc.RSBP,pc.RDBP,pc.ProjectName,
                        pc.Status,pc.ReviewDoctor,CONVERT(pc.ReviewDate,CHAR(19)) ReviewDate
                        from pat_test_checklist pc 
                        WHERE 
                        pc.RequisitionId='{Rid}'
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getUrineTestDetailsByRidAndFic(self, Rid=None, Fic=None) -> dict:
        """
        根据条码及编码大类查询尿检细项
        :param Rid: 条码
        :param Fic: 体检编码大类
        :return:
        """
        sql = f"""
            SELECT 
            pf.ItemCode,pf.ItemName,pf.RequisitionId,pf.Lis_RangeState,pf.FeeItemCode,
            pf.Lis_Result,pf.Lis_ResultUnit,pf.Lis_RangeHighValue,pf.Lis_RangeLowValue,
            CONVERT(pf.ReceivedTime,CHAR(19)) 'ReceivedTime'
            from pat_test_result pf 
            WHERE 
            pf.RequisitionId='{Rid}' and pf.FeeItemCode='{Fic}'

           """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getEcgDetails(self, RequisitionId: str, FeeItemCode: str):
        """
        根据条码及编码大类查询心电图
        @param RequisitionId:
        @param FeeItemCode:
        @return:
        """
        sql = f"""
                        SELECT 
                        pf.ECG_ExaminationsConlc,pf.ECG_ExaminationsFind,pf.ECG_Reportopter,
                        pf.RequisitionId,pf.FeeItemCode,
                        CONVERT(pf.ECG_ReportTime,CHAR(19)) 'ECG_ReportTime'
                        from pat_test_result pf 
                        WHERE 
                        pf.RequisitionId='{RequisitionId}' and pf.FeeItemCode='{FeeItemCode}'
                       """
        _RES = self.SqlSelectByOneOrList(sql=sql, type=1)
        return _RES

    def we_getAbdomenDetails(self, RequisitionId: str, FeeItemCode: str):
        """
        根据条码及编码大类查询腹部超声
        @param RequisitionId: 体检条码
        @param FeeItemCode: 项目编码
        @return:
        """
        sql = f"""
                        SELECT 
                        pf.PACS_Auditopter,pf.PACS_ExaminationsConlc,pf.PACS_ExaminationsFind,
                        pf.PACS_PhotoUID,pf.PACS_ExaminationsParts,pf.RequisitionId,pf.FeeItemCode,
                        pf.PACS_Auditopter,pf.PACS_Positive,
                        CONVERT(pf.PACS_AuditTime,CHAR(19)) 'PACS_AuditTime',
                        CONVERT(pf.PACS_CheckTime,CHAR(19)) 'PACS_CheckTime',
                        CONVERT(pf.PACS_RegistTime,CHAR(19)) 'PACS_RegistTime',
                        CONVERT(pf.PACS_ReportTime,CHAR(19)) 'PACS_ReportTime'
                        from pat_test_result pf WHERE 
                        pf.RequisitionId='{RequisitionId}' and pf.FeeItemCode='{FeeItemCode}'
                       """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def we_getUrineTestItemListByRequisitionId(self, RequisitionId=None, userId=None) -> dict:
        """
        :param userId: 是否知道体检条码，如果没有传入条码，则根据个人序号进行取当前年最新一条条码记录
        :param RequisitionId: 体检条码
        :return:
        """
        try:
            sql = f"""
                SELECT pf.RequisitionId,pf.BarCode,pf.ApplyDoctorName,
                pf.ApplyDoctorNo,pf.FeeItemCode,pf.FeeItemName,CONVERT(pf.ApplyDate,CHAR(19)) 'ApplyDate'
                 from pat_test_form  pf WHERE pf.RequisitionId='{RequisitionId}'
                """
            _res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if _res.get('status') == 200:
                _res.get('result').insert(0, {"RequisitionId": RequisitionId, "FeeItemName": "基本情况", "FeeItemCode": 0})
            return _res
        except Exception as e:
            print(f"getUrineTestItemListByRequisitionId:{e}")

    def we_getPhysicalExamListSql(self, userId, page=1, limit=50) -> dict:
        """
        :param userId: 用户ID
        :param page: 分页获取
        :param limit: 每页条目
        :return:
        """
        try:
            _SqlGetPhysicalExamList = f"""
               select c.RequisitionId,c.userId,c.org_code,c.ProjectName,c.ProjectNo,
               CONVERT(c.VisitingDate,CHAR(19)) 'VisitingDate',c.Operator
               from pat_test_checklist c where userId ={userId}  order by c.Did desc 
               limit {(page - 1) * limit},{limit} 
               """
            _res = self.SqlSelectByOneOrList(sql=_SqlGetPhysicalExamList, type=1)
            return _res
        except Exception as e:
            print(f"getPhysicalExamListSql:{e}")

    def we_registerSql(self, pwd: str, nick: str, idCard: str) -> dict:  # 注册验证
        """
        :param pwd: 密码
        :param nick: 昵称
        :param idCard: 有效证件
        :return:
        """
        res = {"status": 0, "msg": ''}  # 返回数据
        idCardDe = self.SM4.decryptData_ECB(idCard)  # 身份证解密
        try:
            _queryIsExistByIdCard = f"""
               SELECT id,idCard,name from fh_personbasics where idCard='{idCardDe}'
               """
            _queryRes = self.SqlSelectByOneOrList(sql=_queryIsExistByIdCard)
            RESULT = _queryRes.get("result")
            if _queryRes.get('status') == 200:  # 查询身份证成功
                _queryIsRegistered = f"""
                    SELECT a.idCard from fh_personbasics a 
                    join userinfo b on a.id = b.relation where a.idCard='{idCardDe}'
                   """
                _queryIsRegisteredRes = self.SqlSelectByOneOrList(sql=_queryIsRegistered)
                if _queryIsRegisteredRes.get("status") == 200:  # 此时能查询到，说明已经注册过
                    res.update(status=13205, msg="已开通，无需重复")
                elif _queryIsRegisteredRes.get("status") == 13204:  # 此时没能查询到，说明未注册过，可以注册
                    if nick == '':
                        nick = RESULT.get('name')
                    _sqlInsertByRegister = """
                       INSERT INTO userinfo 
                       ( userAccount,name, relation,userPassword,nickName,authority,status) 
                       VALUES ('{}','{}','{}','{}','{}',1,0
                       )

                       """.format(RESULT.get('idCard')[-8:], RESULT.get('name'), RESULT.get('id'), pwd, nick)
                    _res = self.insertSqlReturnId(sql=_sqlInsertByRegister)
                    if _res.get('status') == 200:
                        res.update(status=_res.get('status'), msg="开通成功")
                    else:
                        res.update(status=_res.get('status'), msg=_res.get('msg'))
            elif _queryRes.get('status') == 13204:
                res.update(status=_queryRes.get('status'), msg="用户不存在")
            else:
                res.update(status=_queryRes.get('status'), msg="操作失败")
            return res
        except Exception as e:
            log.logger.error(str(e))
            res.update(status=13203, msg="操作失败，请联系管理员")
            return res

    def we_LoginSql(self, u_name: str, pwd: str) -> dict:  # 登录验证
        """
        @param u_name: 账号
        @param pwd: 密码
        @return: 返回数据类型为json格式，status=200
                表示返回成功，13201表示账号存在，但密码不正确
                13204表示没该账号
                13203 异常错误
        """
        # De_crypto = self.SM4.decryptData_ECB(u_name)
        res = {}  # 返回数据
        EnString = self.SM4.encryptData_ECB(pwd)  # 加密密码
        try:
            SqlUserinfo = f"""
                          SELECT u.userAccount,u.name,u.userPassword,u.authority,u.status,u.relation,u.nickName,
                                  CONVERT(fp.birthday,CHAR(10)) `birthday`,fp.org_name,fp.org_code,fp.gender,fp.userId
                          from 
                          userinfo u join fh_personbasics fp on u.relation = fp.id 
                           where u.userAccount='{u_name}' AND fp.status=0
                          """
            _res = self.SqlSelectByOneOrList(sql=SqlUserinfo)
            if _res.get("status") == 200 and _res.get('result').get("status") in [1, '1']:
                if _res.get('result').get("userPassword") == EnString:
                    result = _res.get('result')
                    result.pop('userPassword', None)  # 删除密码键值，注意：如果pop删除，key不存在会报错，可以设置不存在时返回的值
                    result.pop('status', None)
                    res.update(status=_res.get('status', 200), msg='验证通过', result=result)
                else:
                    res.update(status=13201, msg='密码错误')
            elif _res["status"] == 200 and _res.get('result').get("status") in [0, '0']:
                res.update(status=13204, msg='账号已注销')
            elif _res.get('status') == 13204:
                res.update(status=_res.get('status', 13204), msg='账号不存在')
            else:
                res.update(status=_res.get('status', 13203), msg='未知错误')
            return res
        except Exception as e:
            res.update(status=13203, msg='抱歉，验证出错')
            log.logger.error(str(e))
            return res

    def sys_search_suggestions(self, keyWords):
        """
        搜索建议。搜索姓名时有效，并且只返回前50条数据
        @param keyWords:
        @return:
        """
        sql = f"""
            SELECT sys_user_name ,user_id FROM physical.sys_user 
            WHERE `sys_user_name` LIKE '%{keyWords}%' ORDER BY id DESC LIMIT 50
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def likeSearchSuggestion(self, keyWords):
        """
        搜索建议。搜索姓名时有效，并且只返回前10条数据
        @param keyWords:
        @return:
        """
        sql = f"""
            SELECT name,userId FROM fh_personbasics 
            WHERE `name` LIKE '%{keyWords}%' OR `idCard` LIKE '%{keyWords}%' ORDER BY id DESC LIMIT 50
        """
        return self.SqlSelectByOneOrList(sql=sql, type=1)

    def sys_like_search(self, searchText, page=1, limit=50):
        """
        模糊查询分页-机构
        @param searchText:
        @param page:
        @param limit:
        @return:
        """
        if searchText == '':
            sql = f"""
                        SELECT COUNT(*) `total` FROM sys_user
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 200:
                _res = handleTotal(res)
                sql = f"""
                            SELECT *  FROM sys_user 
                                ORDER BY id DESC  
                                limit {(page - 1) * limit},{limit}
                        """
                res = self.SqlSelectByOneOrList(sql=sql, type=1)
                if res.get("status") == 200:
                    data = res.get('result')
                    _res.update(lt=data)
                    res.update(result=_res)
        else:
            sql = f"""
                        SELECT COUNT(*) `total`  FROM physical.sys_user su 
                        WHERE su.sys_user_name LIKE '%{searchText}%' 
                        OR su.idCard LIKE '%{searchText}%'
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 200:
                _res = handleTotal(res)
                sql = f"""
                        SELECT su.* FROM sys_user  su
                        WHERE su.sys_user_name LIKE '%{searchText}%' 
                        OR su.idCard LIKE '%{searchText}%'
                                ORDER BY id DESC  
                                limit {(page - 1) * limit},{limit}
                """
                res = self.SqlSelectByOneOrList(sql=sql, type=1)
                if res.get('status') == 200:
                    _res.update(lt=res.get('result'))
                    res.update(result=_res)
                    _redis.set(key=f"{searchText}{page}{limit}", value=str(res), timeout=60)
        return res

    def likeSearch(self, searchText, page=1, limit=50):
        """
        模糊查询分页
        @param searchText: 关键字
        @param page: 页码
        @param limit: 数据量
        @return:
        """
        if searchText == '':
            sql = f"""
                        SELECT COUNT(*) `total`  FROM fh_personbasics fp 
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 200:
                _res = handleTotal(res)
                sql = f"""
                    SELECT fp.name,fp.userId,fp.idcard,fp.org_code,fp.org_name,
                            fp.gender,CONVERT(fp.birthday,CHAR(19)) `birthday`,fp.phone,
                            fp.nation,fp.live_type,fp.creator,
                            CONVERT(fp.creatime,CHAR(19)) `creatime`,
                            fp.cur_address `address`,fp.status,fp.blood_type,fp.person_type
                    FROM fh_personbasics fp where fp.name LIKE '%{searchText}%' 
                    OR fp.org_name LIKE '%{searchText}%' 
                    OR fp.idCard LIKE '%{searchText}%' and fp.status=0 
                    ORDER BY fp.id DESC 
                    limit {(int(page) - 1) * int(limit)},{int(limit)}
                """
                res = self.SqlSelectByOneOrList(sql=sql, type=1)
                if res.get("status") == 200:
                    _res.update(lt=res.get('result'))
                    res.update(result=_res)
                    _redis.set(key=f"{searchText}{page}{limit}", value=str(res), timeout=60)
        else:
            sql = f"""
                        SELECT COUNT(*) `total`  FROM fh_personbasics fp 
                        WHERE fp.name LIKE '%{searchText}%' 
                        OR fp.org_name LIKE '%{searchText}%' 
                        OR fp.idCard LIKE '%{searchText}%' and fp.status=0 
                    """
            res = self.SqlSelectByOneOrList(sql=sql)
            if res.get('status') == 200:
                _res = handleTotal(res)
            sql = f"""
                SELECT fp.name,fp.userId,fp.idcard,fp.org_code,fp.org_name,
                        fp.gender,CONVERT(fp.birthday,CHAR(19)) `birthday`,fp.phone,
                        fp.nation,fp.live_type,fp.creator,
                        CONVERT(fp.creatime,CHAR(19)) `creatime`,
                        fp.cur_address `address`,fp.status,fp.blood_type,fp.person_type
                FROM fh_personbasics fp where fp.name LIKE '%{searchText}%' 
                OR fp.org_name LIKE '%{searchText}%' 
                OR fp.idCard LIKE '%{searchText}%' and fp.status=0 
                ORDER BY fp.id DESC 
                limit {(int(page) - 1) * int(limit)},{int(limit)}
            """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get('status') == 200:
                _res.update(lt=res.get('result'))
                res.update(result=_res)
                _redis.set(key=f"{searchText}{page}{limit}", value=str(res), timeout=60)
        return res

    def likeSearchTotal(self, searchText):
        """
        模糊查询结果总数，姓名、身份证、机构
        @param searchText: 模糊文本
        @return:
        """
        sql = f"""
            SELECT COUNT(*) `total` FROM fh_personbasics 
            WHERE `name` LIKE '%{searchText}%' 
            OR org_name LIKE '%{searchText}%' 
            OR idCard LIKE '%{searchText}%'
        """
        return self.SqlSelectByOneOrList(sql=sql)

    def user_details_by_idCard(self, idCard, userId=0):
        """
        通过身份证查询用户详情
        @param idCard:
        @param userId:
        @return:
        """
        sql = f"""
        select fp.id,fp.userId,fp.idCard,fp.name,
        fp.gender,fp.phone,fp.nation,fp.contact_name,
        fp.contact_phone,fp.live_type,fp.blood_type,cur_address,
        fp.org_code,so.org_name,fp.status,fp.creator,fp.last_updator,
        CONVERT(fp.creatime,CHAR(19)) `creatime` ,
            CONVERT(fp.birthday,CHAR(19)) `birthday` ,
            CONVERT(fp.last_updatime,CHAR(19)) `last_updatime`
            FROM fh_personbasics fp left join sys_org so on fp.org_code = so.org_code 
                WHERE fp.idCard='{idCard}' OR fp.userId={userId}
            """
        print(sql)
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            _redis.set(key=f"{idCard}", value=str(_res), timeout=60)
        return _res

    def userDetailsByUserId(self, userId):
        """
        通过用户ID查询用户详情
        @param userId:
        @return:
        """
        sql = f"""
        select fp.id,fp.userId,fp.idCard,fp.name,
        fp.gender,fp.phone,fp.nation,fp.contact_name,
        fp.contact_phone,fp.live_type,fp.blood_type,cur_address,
        fp.org_code,fp.org_name,fp.status,fp.creator,fp.last_updator,
        CONVERT(fp.creatime,CHAR(19)) `creatime` ,
            CONVERT(fp.birthday,CHAR(19)) `birthday` ,
            CONVERT(fp.last_updatime,CHAR(19)) `last_updatime`
            FROM fh_personbasics fp WHERE fp.userId='{userId}'
            """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            _redis.set(key=f"{userId}", value=str(_res), timeout=60)
        return _res

    def userTotal(self, org_id):
        """
        查询当前机构的用户总数
        @param org_id: 机构代码
        @return:
        """
        sql = f"""
            select COUNT(*) `total` FROM fh_personbasics WHERE org_code='{org_id}'
            """
        return self.SqlSelectByOneOrList(sql=sql)

    def getUserListByOrgId(self, org_id, page=1, limit=50):
        """
        查询当前机构的用户信息
        @param limit:
        @param page:
        @param org_id:
        @return:
        """
        sql = f"""
                SELECT COUNT(*) `total` FROM fh_personbasics fp where fp.status=0 and fp.org_code='{org_id}'
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            _res = handleTotal(res)
            sql = f"""
                SELECT fp.name,fp.userId,fp.idcard,fp.org_code,fp.org_name,
                        fp.gender,CONVERT(fp.birthday,CHAR(19)) `birthday`,fp.phone,
                        fp.nation,fp.live_type,fp.creator,
                        CONVERT(fp.creatime,CHAR(19)) `creatime`,fp.cardId,
                        fp.cur_address `address`,fp.status,fp.blood_type,fp.person_type
                FROM fh_personbasics fp where fp.status=0 and fp.org_code='{org_id}'
                ORDER BY fp.id DESC 
                limit {(int(page) - 1) * int(limit)},{int(limit)}
            """
            res = self.SqlSelectByOneOrList(sql=sql, type=1)
            if res.get('status') == 200:
                _res.update(lt=res.get('result'))
                res.update(result=_res)
                _redis.set(key=f"{org_id}{page}{limit}", value=str(res), timeout=60)
        return res

    def sys_login(self, userAccount, userPassword):
        """
        用户登录
        @param userAccount:
        @param userPassword:
        @return:
        """
        # 检查账号是否存在
        sql = f"""
                SELECT su.sys_user_account,su.user_id,su.org_id,
                su.sys_user_name,su.authority,su.sys_user_password,su.status
                FROM sys_user su 
                where su.sys_user_account='{userAccount}'
                """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            if _res.get('result').get('status') in [1, '1']:
                password = self.SM4.encryptData_ECB(plain_text=userPassword)
                if _res.get('result').get('sys_user_password') == password:
                    resultDict = {}
                    authority = _res.get('result').get('authority')
                    menuList = self.menuSysList(authority=authority)
                    resultDict['username'] = _res.get('result').get('sys_user_account')
                    resultDict['name'] = _res.get('result').get('sys_user_name')
                    resultDict['user_id'] = _res.get('result').get('user_id')
                    resultDict['org_id'] = _res.get('result').get('org_id')
                    # resultDict['password'] = _res.get('result').get('userPassword')
                    resultDict['menu'] = menuList
                    _res.update(status=200, msg='登录成功', result=resultDict)
                else:
                    _res.update(msg="密码错误", status=13201)
                    _res.pop('result')
            else:
                _res.update(status=13202, msg='用户已被禁用')
                _res.pop('result')
        elif _res.get('status') == 13204:
            _res.update(msg=f"账号{userAccount}不存在")
        else:
            _res.update(msg="登录失败，请稍后重试")
        return _res

    def login(self, userAccount, userPassword):
        """
        用户登录
        @param userAccount:
        @param userPassword:
        @return:
        """
        # 检查账号是否存在
        sql = f"""
                SELECT su.sys_user_account,su.user_id,su.org_id,
                su.sys_user_name,su.authority,su.sys_user_password,su.status
                FROM sys_user su 
                where su.sys_user_account='{userAccount}'
                """
        _res = self.SqlSelectByOneOrList(sql=sql)
        if _res.get('status') == 200:
            if _res.get('result').get('status') in [1, '1']:
                password = self.SM4.encryptData_ECB(plain_text=userPassword)
                if _res.get('result').get('sys_user_password') == password:
                    resultDict = {}
                    authority = _res.get('result').get('authority')
                    menuList = self.menuList(authority=authority)
                    resultDict['username'] = _res.get('result').get('sys_user_account')
                    resultDict['name'] = _res.get('result').get('sys_user_name')
                    resultDict['user_id'] = _res.get('result').get('user_id')
                    resultDict['org_id'] = _res.get('result').get('org_id')
                    # resultDict['password'] = _res.get('result').get('userPassword')
                    resultDict['menu'] = menuList
                    _res.update(status=200, msg='登录成功', result=resultDict)
                else:
                    _res.update(msg="密码错误", status=13201)
                    _res.pop('result')
            else:
                _res.update(status=13202, msg='用户已被禁用')
                _res.pop('result')
        elif _res.get('status') == 13204:
            _res.update(msg=f"账号{userAccount}不存在")
        else:
            _res.update(msg="登录失败，请稍后重试")
        return _res

    def menuSysList(self, authority):
        # 获得数据库连接池
        conn = self.DbConnect_Pool.connection()
        conn.ping(reconnect=True)
        cur = conn.cursor()
        col = """SHOW COLUMNS FROM sys_menu"""
        cur.execute(col)
        conn.commit()
        index = cur.fetchall()  # 返回字段
        _index = [x[0] for x in index]
        try:
            SqlMenuList = """
                            SELECT * from sys_menu
                            """
            cur.execute(SqlMenuList)
            conn.commit()
            result = cur.fetchall()
            Menu = []
            resultList = []
            if result:  # 返回不为空
                for item in result:
                    resultDict = {}
                    for i in range(len(_index)):
                        resultDict[_index[i]] = item[i]
                    authorityNum = resultDict['authority'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(authorityNum)
                    if str(authority) in itemResult:
                        resultList.append(resultDict)
                        resultDict.pop('authority', None)
                        # del resultDict['authority']  # 删除权限的键值
                for item in resultList:
                    lst = []
                    ite = item['children'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(ite)
                    for it in itemResult:
                        for items in resultList:
                            if items['menuid'] == int(it):
                                lst.append(items)
                                item['children'] = lst
                                # del item['path']
                                # del item['name']
                                # del item['component']
                                if item not in Menu:
                                    Menu.append(item)
            return Menu
        except Exception as e:
            log.logger.error(str(e))
            conn.close()
            cur.close()
            print(e)

    def menuList(self, authority):
        # 获得数据库连接池
        conn = self.DbConnect_Pool.connection()
        conn.ping(reconnect=True)
        cur = conn.cursor()
        col = """SHOW COLUMNS FROM menulist"""
        cur.execute(col)
        conn.commit()
        index = cur.fetchall()  # 返回字段
        _index = [x[0] for x in index]
        try:
            SqlMenuList = """
                           SELECT * from physical.menulist
                           """
            cur.execute(SqlMenuList)
            conn.commit()
            result = cur.fetchall()
            Menu = []
            resultList = []
            if result:  # 返回不为空
                for item in result:
                    resultDict = {}
                    for i in range(len(_index)):
                        resultDict[_index[i]] = item[i]
                    authorityNum = resultDict['authority'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(authorityNum)
                    if str(authority) in itemResult:
                        resultList.append(resultDict)
                        resultDict.pop('authority', None)
                        # del resultDict['authority']  # 删除权限的键值
                for item in resultList:
                    lst = []
                    ite = item['children'].replace("'", '')
                    pattern = re.compile('\d+')
                    itemResult = pattern.findall(ite)
                    for it in itemResult:
                        for items in resultList:
                            if items['menuid'] == int(it):
                                lst.append(items)
                                item['children'] = lst
                                # del item['path']
                                # del item['name']
                                # del item['component']
                                if item not in Menu:
                                    Menu.append(item)
            return Menu
        except Exception as e:
            log.logger.error(str(e))
            conn.close()
            cur.close()
            print(e)

    def test(self):

        sql = """
        SELECT uf.* FROM userinfo uf  where uf.id=25 limit 1
        """
        return self.SqlSelectByOneOrList(sql=sql)

    @staticmethod
    def getInsertId(cur):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        cur.execute("SELECT @@IDENTITY AS id")
        result = cur.fetchall()
        _dist = result[0]
        return _dist[0]

    def insertSqlReturnId(self, sql) -> dict:

        """
        新增，并且返回当前新增的id
        @param sql: 操作语句
        @return: id
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                insertId = self.getInsertId(cur=cur)
                if insertId not in [0, '0', None]:
                    _sqlRes.update(status=200, msg='操作成功', insertId=insertId)
                else:
                    _sqlRes.update(status=13203, msg='操作失败')
                    conn.rollback()
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            print(e)
            _sqlRes.update(status=13203, msg="数据库连接错误")
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def insertOrUpdateOrDeleteBySqlList(self, sqlList):
        """
        多条语句新增修改，删除
        @param sqlList:
        @return:
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                for index, item in enumerate(sqlList):
                    cur.execute(item)
                    conn.commit()
                _sqlRes.update(status=200, msg='操作成功', row=cur.rowcount)
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            print(e)
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def insertOrUpdateOrDeleteBySql(self, sql):
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                _sqlRes.update(status=200, msg='操作成功', row=cur.rowcount)
            else:
                _sqlRes.update(status=status, msg='数据库连接错误')
        except Exception as e:
            print(e)
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def getLastRequisitionIdOrBarCode(self, TYPE='R'):
        """
        获取最新的RequisitionId
        @param TYPE: 类型，R-流水号，B-体检编码
        @return:
        """
        sql = f"""
                SELECT zs.serialnumber  FROM zd_sysseed zs  
                WHERE zs.field='{"RequisitionId" if TYPE == "R" else "barCode"}'
            """
        res = self.SqlSelectByOneOrList(sql=sql)
        if res.get('status') == 200:
            return int(res.get('result').get("serialnumber"))
        else:
            return False

    def updateLastRequisitionIdOrBarCode(self, updateValue, TYPE='R'):
        """
        更新最后的RequisitionId或者barCode
        @param updateValue: 最新的
        @param TYPE: 类型，R-流水号，B-体检编码
        @return:
        """
        sql = f"""
                    UPDATE  zd_sysseed SET serialnumber='{updateValue}' 
                    WHERE field='{"RequisitionId" if TYPE == "R" else "barCode"}'
                """
        res = self.insertOrUpdateOrDeleteBySql(sql=sql)
        if res.get("status") == 200:
            return True
        else:
            return False

    def getLastUserId(self):
        """
        查询最大的用户ID进行自增
        @return:
        """
        Sql = """
        SELECT userId FROM user_list ORDER BY userId DESC LIMIT 1
        """
        res = self.SqlSelectByOneOrList(sql=Sql)
        if res.get('status') == 200:
            userId = res.get('result').get('userId')
            if userId:
                return int(userId) + 1
        else:
            return 13204

    def db_init(self):
        try:
            cfg = ConfigParser()
            cfg.read(DB_CONFIG_PATH)
            DB_HOST = cfg.get('database', 'DB_HOST')
            DB_PORT = 3306
            DB_USER = cfg.get('database', 'DB_USER')
            DB_PASSWORD = cfg.get('database', 'DB_PASSWORD')
            DB_NAME = cfg.get('database', 'DB_NAME')
            DB_CHARSET = "utf8"
            DbConnect_Pool = PooledDB(pymysql,
                                      5,
                                      charset=DB_CHARSET,
                                      host=DB_HOST,
                                      user=DB_USER,
                                      passwd=DB_PASSWORD,
                                      db=DB_NAME,
                                      port=int(DB_PORT)
                                      )
            return DbConnect_Pool
        except Exception as e:
            log.logger.error(str(e))
            print(f"初始化V3数据库失败：{e}")

    def init_conn_cur_index(self):
        try:
            if self.DbConnect_Pool:
                conn = self.DbConnect_Pool.connection()
                conn.ping(reconnect=True)
                cur = conn.cursor(pymysql.cursors.DictCursor)  # 获取游标,pymysql.cursors.DictCursor设置返回结果为字典类型
                return 200, conn, cur
            else:
                return 13203, None, None
        except Exception as e:
            log.logger.error(str(e))
            return 13203, None, None

    def selectByFaceId(self, faceId) -> dict:
        sql = f"""
         SELECT userName,faceStatus FROM user_list WHERE faceId={faceId}
        """
        return self.SqlSelectByOneOrList(sql)

    def SqlListSelectByOneOrList(self, sqlList: list, oldData: list) -> dict:
        """
        功能：通过多条条语句查询
        @param oldData:
        @param sqlList:
        @param sql: 操作语句列表
        @param type: 0 返回一条，1返回多条
        @return:
        """
        conn, cur = None, None
        new_data = oldData
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                for index, sql in enumerate(sqlList):
                    cur.execute(sql)
                    conn.commit()
                    rows = cur.fetchall()
                    if rows:
                        new_data[index].update(apply_type=rows)
                _sqlRes.update(status=200, msg='获取成功', result=new_data)
                # else:
                #     _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='操作失败')
        except Exception as e:
            log.logger.error(str(e))
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def select_by_sqlList(self, sqlList: list):
        """
        多条语句查询，返回字典列表
        @param sqlList:
        @return:
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                arraylist = []
                for itemDict in sqlList:
                    cur.execute(itemDict.get('sql'))
                    conn.commit()
                    rows = cur.fetchall()
                    _dict = {}
                    if rows:
                        key = itemDict.get('key', 0)
                        _dict['list'] = rows
                        _dict['FeeItemName'] = rows[0].get('FeeItemName', '-')
                        _dict['FeeItemCode'] = key
                        arraylist.append(_dict)
                if arraylist:
                    _sqlRes.update(status=200, msg='获取成功', result=arraylist)
                else:
                    _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='操作失败')
        except Exception as e:
            log.logger.error(str(e))
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes

    def SqlSelectByOneOrList(self, sql, type=0) -> dict:
        """
        功能：通过一条语句查询
        @param sql: 操作语句
        @param type: 0 返回一条，1返回多条
        @return:
        """
        conn, cur = None, None
        _sqlRes = {"status": 0, "msg": ''}  # 返回数据
        try:
            status, conn, cur = self.init_conn_cur_index()  # 获取操作对象
            if status == 200:
                cur.execute(sql)
                conn.commit()
                rows = cur.fetchall()
                if rows:
                    _sqlRes.update(status=200, msg='获取成功', result=rows[0] if type == 0 else rows)
                else:
                    _sqlRes.update(status=13204, msg='无数据')
            else:
                _sqlRes.update(status=status, msg='操作失败')
        except Exception as e:
            log.logger.error(str(e))
            conn.rollback()
            _sqlRes.update(status=13203, msg=e)
        finally:
            if conn and cur:
                cur.close()
                conn.close()
            return _sqlRes
