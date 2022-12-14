from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.crypto import _MD5
from utils.dbV3.db import database
import ast
from utils.log.log import Logger
from utils.redisCache.redisCache import Redis
from utils.identity.creatInfo import creat_user_info

_redis = Redis()
sm4 = _MD5.SM4Utils()  # 实例化sm4加密
db = database()  # 实例化数据库
log = Logger()


def errorRes(status=13203, msg='请求错误'):
    """
    返回请求错误
    """
    return {'status': status, 'msg': msg}


class delete_card_by_userId_View(APIView):
    """
    根据用户Id进行绑定卡
    请求方式：GET
    参数：userId，cardId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId', 0)
            cardId = request.query_params.get('cardId', 0)
            return Response(db.delete_card_by_userId(userId=userId,cardId=cardId))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class add_card_by_userId_View(APIView):
    """
    根据用户Id进行绑定卡
    请求方式：GET
    参数：userId，cardId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId', 0)
            cardId = request.query_params.get('cardId', 0)
            return Response(db.add_card_by_userId(userId=userId, cardId=cardId))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_upload_list_View(APIView):
    """
    获取体检上传
    请求方式：GET
    参数：limit=20,page=1
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            limit = request.query_params.get('limit', 20)
            page = request.query_params.get('page', 1)
            return Response(db.get_upload_list(limit=int(limit), page=int(page)))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_exam_echarts_View(APIView):
    """
    获取体检量化数据
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            return Response(db.get_exam_echarts())
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_org_code_echarts_View(APIView):
    """
    获取机构量化数据
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            return Response(db.get_org_code_echarts())
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_apply_data_total_View(APIView):
    """
    获取申请总数
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            return Response(db.get_apply_data_total())
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_exam_data_total_View(APIView):
    """
    获取体检审核等总数
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            return Response(db.get_exam_data_total())
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_care_view(APIView):
    """
    根据rid查询自理评估
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId')
            rid = request.query_params.get('rid')
            return Response(db.get_care(userId=userId, rid=rid))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class add_or_update_selfCare_view(APIView):
    """
    新增自理评估
    请求方式：POST
    参数：
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            userId = request.data.get('userId', 0)
            org_code = request.data.get('org_code', 0)
            final_point = request.data.get('final_point', 0)
            care_assess_level = request.data.get('care_assess_level', 0)
            RequisitionId = request.data.get('RequisitionId', 0)
            doc_code = request.data.get('doc_code', '')
            qus_id_1 = request.data.get('qus_id_1', '')
            qus_id_2 = request.data.get('qus_id_2', '')
            qus_id_3 = request.data.get('qus_id_3', '')
            qus_id_4 = request.data.get('qus_id_4', '')
            qus_id_5 = request.data.get('qus_id_5', '')

            params.update(userId=userId, org_code=org_code, final_point=final_point,
                          care_assess_level=care_assess_level,
                          RequisitionId=RequisitionId, doc_code=doc_code,
                          qus_id_1=qus_id_1, qus_id_2=qus_id_2,
                          qus_id_3=qus_id_3, qus_id_4=qus_id_4, qus_id_5=qus_id_5,
                          )
            return Response(db.add_or_update_care(params=params))
            # return Response(errorRes(msg='请求失败，请联系管理员!'))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_depression_view(APIView):
    """
    根据rid查询用户信息及抑郁评估
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId')
            rid = request.query_params.get('rid')
            return Response(db.get_depression(userId=userId, rid=rid))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class add_or_update_depression_view(APIView):
    """
    新增抑郁评估
    请求方式：POST
    参数：
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            userId = request.data.get('userId', 0)
            org_code = request.data.get('org_code', 0)
            final_point = request.data.get('final_point', 0)
            depression_assesss_level = request.data.get('depression_assesss_level', 0)
            RequisitionId = request.data.get('RequisitionId', 0)
            doc_code = request.data.get('doc_code', 0)
            qus_id_1 = request.data.get('qus_id_1', 2)
            qus_id_2 = request.data.get('qus_id_2', 2)
            qus_id_3 = request.data.get('qus_id_3', 2)
            qus_id_4 = request.data.get('qus_id_4', 2)
            qus_id_5 = request.data.get('qus_id_5', 2)
            qus_id_6 = request.data.get('qus_id_6', 2)
            qus_id_7 = request.data.get('qus_id_7', 2)
            qus_id_8 = request.data.get('qus_id_8', 2)
            qus_id_9 = request.data.get('qus_id_9', 2)
            qus_id_10 = request.data.get('qus_id_10', 2)
            qus_id_11 = request.data.get('qus_id_11', 2)
            qus_id_12 = request.data.get('qus_id_12', 2)
            qus_id_13 = request.data.get('qus_id_13', 2)
            qus_id_14 = request.data.get('qus_id_14', 2)
            qus_id_15 = request.data.get('qus_id_15', 2)
            qus_id_16 = request.data.get('qus_id_16', 2)
            qus_id_17 = request.data.get('qus_id_17', 2)
            qus_id_18 = request.data.get('qus_id_18', 2)
            qus_id_19 = request.data.get('qus_id_19', 2)
            qus_id_20 = request.data.get('qus_id_20', 2)
            qus_id_21 = request.data.get('qus_id_21', 2)
            qus_id_22 = request.data.get('qus_id_22', 2)
            qus_id_23 = request.data.get('qus_id_23', 2)
            qus_id_24 = request.data.get('qus_id_24', 2)
            qus_id_25 = request.data.get('qus_id_25', 2)
            qus_id_26 = request.data.get('qus_id_26', 2)
            qus_id_27 = request.data.get('qus_id_27', 2)
            qus_id_28 = request.data.get('qus_id_28', 2)
            qus_id_29 = request.data.get('qus_id_29', 2)
            qus_id_30 = request.data.get('qus_id_30', 2)

            params.update(userId=userId, org_code=org_code, final_point=final_point,
                          depression_assesss_level=depression_assesss_level,
                          RequisitionId=RequisitionId, doc_code=doc_code,
                          qus_id_1=qus_id_1, qus_id_2=qus_id_2,
                          qus_id_3=qus_id_3, qus_id_4=qus_id_4, qus_id_5=qus_id_5,
                          qus_id_6=qus_id_6, qus_id_7=qus_id_7, qus_id_8=qus_id_8,
                          qus_id_9=qus_id_9, qus_id_10=qus_id_10, qus_id_11=qus_id_11,
                          qus_id_12=qus_id_12, qus_id_13=qus_id_13, qus_id_14=qus_id_14,
                          qus_id_15=qus_id_15, qus_id_16=qus_id_16, qus_id_17=qus_id_17,
                          qus_id_18=qus_id_18, qus_id_19=qus_id_19, qus_id_20=qus_id_20,
                          qus_id_21=qus_id_21, qus_id_22=qus_id_22, qus_id_23=qus_id_23,
                          qus_id_24=qus_id_24, qus_id_25=qus_id_25, qus_id_26=qus_id_26,
                          qus_id_27=qus_id_27, qus_id_28=qus_id_28, qus_id_29=qus_id_29,
                          qus_id_30=qus_id_30,
                          )
            return Response(db.add_or_update_depression(params=params))
            # return Response(errorRes(msg='请求失败，请联系管理员!'))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class add_user_view(APIView):
    """
    新增用户
    请求方式：POST
    参数：
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            cur_address = request.data.get('address', 0)
            birthday = request.data.get('birthday', 0)
            blood_type = request.data.get('blood_type', 0)
            gender = request.data.get('gender', 0)
            idCard = request.data.get('idcard', 0)
            nation = request.data.get('nation', 0)
            live_type = request.data.get('live_type', 0)
            name = request.data.get('name', 0)
            org_code = request.data.get('org_name', 0)
            person_type = request.data.get('person_type', 0)
            phone = request.data.get('phone', 0)
            status = request.data.get('status', 0)
            creator = request.data.get('creator', 0)
            params.update(cur_address=cur_address, birthday=birthday, blood_type=blood_type, gender=gender,
                          idCard=idCard, live_type=live_type, name=name, org_code=org_code, person_type=person_type,
                          phone=phone, status=status, creator=creator, nation=nation)
            return Response(db.pc_add_user(params=params))
            # return Response(errorRes(msg='请求失败，请联系管理员!'))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_sys_user_info_view(APIView):
    """
    根据id查询用户信息
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId')
            return Response(db.query_user_info(userId=userId))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class delete_user_view(APIView):
    """
    删除用户
    请求方式：POST
    参数：list
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            userList = request.data.get('list')
            userList = ast.literal_eval(userList)
            print(request.data)
            print(userList)
            return Response(db.delete_user(userList=userList))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class delete_sys_user_view(APIView):
    """
    删除系统用户
    请求方式：POST
    参数：list
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            userList = request.data.get('list')
            userList = ast.literal_eval(userList)
            return Response(db.delete_sys_user(userList=userList))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class update_sys_user_view(APIView):
    """
    新增系统用户
    请求方式：POST
    参数：org_id: 'Y',
        idCard: 'Y',
        phone: 'Y',
        user_id: '',
        userName: 'Y',
        userAccount: 'Y',
        userPassword: 'Y',
        status: true,
        sys_type: 'Y',
        create_by: 'Y',
        authority: 'Y',
        gender: Y,
        birthday: 'Y'
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            org_id = request.data.get('org_id')
            idCard = request.data.get('idCard')
            phone = request.data.get('phone')
            userName = request.data.get('userName')
            userAccount = request.data.get('userAccount')
            userPassword = request.data.get('userPassword')
            status = request.data.get('status')
            sys_type = request.data.get('sys_type')
            create_by = request.data.get('create_by')
            authority = request.data.get('authority')
            gender = request.data.get('gender')
            birthday = request.data.get('birthday')
            if status == 'true':
                status = 1
            else:
                status = 0
            params.update(org_id=org_id, idCard=idCard, phone=phone, userName=userName, userAccount=userAccount,
                          status=status, sys_type=sys_type, create_by=create_by, authority=authority, gender=gender,
                          birthday=birthday, userPassword=userPassword)
            return Response(db.update_sys_user(params=params))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class add_sys_user_view(APIView):
    """
    新增系统用户
    请求方式：POST
    参数：org_id: 'Y',
        idCard: 'Y',
        phone: 'Y',
        user_id: '',
        userName: 'Y',
        userAccount: 'Y',
        userPassword: 'Y',
        status: true,
        sys_type: 'Y',
        create_by: 'Y',
        authority: 'Y',
        gender: Y,
        birthday: 'Y'
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            org_id = request.data.get('org_id')
            idCard = request.data.get('idCard')
            phone = request.data.get('phone')
            userName = request.data.get('userName')
            userAccount = request.data.get('userAccount')
            userPassword = request.data.get('userPassword')
            status = request.data.get('status')
            sys_type = request.data.get('sys_type')
            create_by = request.data.get('create_by')
            authority = request.data.get('authority')
            gender = request.data.get('gender')
            birthday = request.data.get('birthday')
            if status == 'true':
                status = 1
            else:
                status = 0
            params.update(org_id=org_id, idCard=idCard, phone=phone, userName=userName, userAccount=userAccount,
                          status=status, sys_type=sys_type, create_by=create_by, authority=authority, gender=gender,
                          birthday=birthday, userPassword=userPassword)
            return Response(db.add_sys_user(params=params))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class creat_user_info_view(APIView):
    """
    随机生成用户信息
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            res = creat_user_info()
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_sys_org_list_view(APIView):
    """
    查询系统机构列表
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            res = db.query_sys_org_list()
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_sys_user_view(APIView):
    """
    查询系统用户
    请求方式：GET
    参数：page=1, limit=20
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            page = request.query_params.get('page')
            limit = request.query_params.get('limit')
            res = db.query_sys_user(page=int(page) if page else 1, limit=int(limit) if limit else 20)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class apply_by_userId_view(APIView):
    """
    添加用户申请
    请求方式：GET
    参数：userId, apply_type
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get('userId')
            apply_type = request.query_params.get('apply_type')
            res = db.we_insert_apply_by_userId(userId=userId, apply_type=apply_type)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_user_details_by_idCard_view(APIView):
    """
       通过身份证查询用户基本信息与体检项目类型
    请求方式：get
    参数：idCard,org_code
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            idCard = request.query_params.get('idCard', 0)
            print(idCard)
            org_code = request.query_params.get('org_code', 0)
            res = db.query_user_details_by_idCard(idCard=idCard, org_code=org_code)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class exam_result_upload_rid_view(APIView):
    """
    根据体检编码上传体检结果
    请求方式：get
    参数：rid, uploadStatus: 0-未上传，1-已上传，-1-驳回，[remark: 驳回原因]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            rid = request.query_params.get('rid')
            # remark = request.query_params.get('remark', 0)
            uploadStatus = request.query_params.get('uploadStatus')
            res = db.exam_result_upload_by_rid(rid=rid, uploadStatus=uploadStatus)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class exam_result_audit_by_rid_view(APIView):
    """
   医生审核体检结果
    请求方式：get
    参数：RequisitionId, status: 0-未审核，1-已审核，-1-不通过，[remark: 不通过原因]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            remark = request.query_params.get('remark')
            status = request.query_params.get('status')
            res = db.exam_result_audit_by_rid(rid=RequisitionId, status=status, remark=remark)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_feeItemCode_list_view(APIView):
    """
    查询编码大类列表
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            res = db.select_feeItemCode_list()
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_exam_base_and_urine_by_rid_view(APIView):
    """
   通过体检编码查询体检结果
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            res = db.query_exam_base_and_urine_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class check_exam_type_btn_by_rid_view(APIView):
    """
   根据体检编码校验是否前端可以生成数据，要与选择体检的项目一致
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            res = db.check_exam_type_btn_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class insert_exam_urine_by_rid_view(APIView):
    """
    根据体检编码新增尿检结果
    请求方式：get
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            data = ast.literal_eval(request.query_params.get('data'))
            res = db.insert_exam_urine_by_rid(rid=RequisitionId, params=data.get('data'))
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_exam_base_by_rid_view(APIView):
    """
    通过体检编码查询基本体检结果
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get("RequisitionId")
            res = db.query_exam_base_by_rid(rid=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_exam_upload_by_org_code_view(APIView):
    """
    搜根据机构编码查询体检上传
    请求方式：GET
    参数：org_code, [page=1, limit=20]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            if page and org_code and limit:
                res = db.query_exam_upload_by_org_code(org_code=org_code, page=int(page), limit=int(limit))
            elif page and org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code, page=int(page))
            elif limit and org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code, limit=int(limit))
            elif org_code:
                res = db.query_exam_upload_by_org_code(org_code=org_code)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class get_cache_base_exam(APIView):
    """
    获取缓存中的体检数据
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get('RequisitionId')
            _res = db.query_user_info_by_rid(rid=RequisitionId)
            cache_data = _redis.get(key=f"cache{RequisitionId}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
                if _res.get('status') == 200:
                    result = _res.get('result')
                    res.update(result)
                data = {'status': 200, 'msg': '获取成功', 'result': res}
            else:
                data = {'status': 13204, 'msg': '无数据'}
            return Response(data)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class cache_base_exam(APIView):
    """
    新增基本体检结果
    请求方式：POST
    参数：RequisitionId,Height,Weight,BMI,Temperature,heart_rate
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            data = {}
            RequisitionId = request.data.get('RequisitionId')
            Height = request.data.get('Height')
            Weight = request.data.get('Weight')
            BMI = request.data.get('BMI')
            Temperature = request.data.get('Temperature')
            heart_rate = request.data.get('heart_rate')
            # cache_data = _redis.get(key=f"cache{RequisitionId}")
            # if cache_data:  # 查询缓存是否有数据
            #     cache_data = bytes.decode(cache_data)
            #     res = ast.literal_eval(cache_data)
            #
            data.update(RequisitionId=RequisitionId, Height=Height, Weight=Weight, BMI=BMI,
                        Temperature=Temperature, heart_rate=heart_rate)
            key = f'cache{RequisitionId}'
            _redis.set(key=key, value=str(data), timeout=60 * 60 * 24 * 30)
            return Response(errorRes(msg='保存成功', status=200))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class insert_base_exam(APIView):
    """
    新增基本体检结果
    请求方式：POST
    参数：base_data:{RequisitionId, userId, org_code,
         ProjectNo,ProjectName, RSBP, RDBP,Height,
                    Weight, BMI, Temperature, Operator, VisitingDate,
                    Status,
                    LSBP, LDBP, heart_rate}
    返回：
    """

    def post(self, request, *args, **kwargs):
        try:
            params = {}
            print(222, request.data)
            RequisitionId = request.data.get('RequisitionId')
            userId = request.data.get('userId')
            org_code = request.data.get('org_code')
            Weight = request.data.get('Weight')
            Height = request.data.get('Height')
            BMI = request.data.get('BMI')
            LSBP = request.data.get('LSBP')
            LDBP = request.data.get('LDBP')
            heart_rate = request.data.get('heart_rate')
            Temperature = request.data.get('Temperature')
            VisitingDate = request.data.get('VisitingDate')
            Operator = request.data.get('Operator')
            params.update(RequisitionId=RequisitionId, userId=userId, org_code=org_code,
                          Weight=Weight, Height=Height, BMI=BMI, LSBP=LSBP, LDBP=LDBP,
                          heart_rate=heart_rate, Temperature=Temperature, VisitingDate=VisitingDate,
                          Operator=Operator
                          )
            res = db.insert_base_exam(params=params)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_person_physical_list_by_RequisitionId_view(APIView):
    """
    根据当次体检编码查询当前用户需要体检的项目大类
    请求方式：GET
    参数：RequisitionId
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            RequisitionId = request.query_params.get("RequisitionId")
            res = db.select_person_physical_list_by_RequisitionId(RequisitionId=RequisitionId)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class update_apply_by_id_view(APIView):
    """
    更新用户的申请状态
    请求方式：GET
    参数：Id,apply_status,apply_reason,operator_id
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            Id = request.query_params.get("Id")
            apply_status = request.query_params.get("apply_status")
            apply_reason = request.query_params.get("apply_reason")
            operator_id = request.query_params.get("operator_id")
            res = db.update_apply_by_id(Id=int(Id), apply_status=int(apply_status),
                                        apply_reason=apply_reason if apply_reason else None,
                                        operator_id=operator_id)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_itemCode_list_by_feeItemCode_view(APIView):
    """
    根据大类编码查询细项编码列表
    请求方式：GET
    参数：feeItemCode
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            feeItemCode = request.query_params.get("feeItemCode")
            res = db.select_itemCode_list_by_feeItemCode(feeItemCode=feeItemCode)
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_feeItemCode_list_view(APIView):
    """
    查询编码大类列表
    请求方式：GET
    参数：
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            res = db.select_feeItemCode_list()
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class query_apply_by_text_view(APIView):
    """
    搜索。支持姓名，机构名称，身份证
    请求方式：GET
    参数：searchText, [page=1, limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            cache_data = _redis.get(key=f"searchApply{searchText}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and searchText and limit:
                res = db.query_apply_by_text(searchText=searchText, page=int(page), limit=int(limit))
            elif page and searchText:
                res = db.query_apply_by_text(searchText=searchText, page=int(page))
            elif limit and searchText:
                res = db.query_apply_by_text(searchText=searchText, limit=int(limit))
            elif searchText:
                res = db.query_apply_by_text(searchText=searchText)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class select_apply_by_org_code_view(APIView):
    """
    通过机代码查询用户申请列表
    请求方式：GET
    参数：org_code, [page=1, limit=50，timestamp-时间戳，添加时可以解决缓存问题]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            timestamp = request.query_params.get("timestamp")
            limit = request.query_params.get("limit")
            if timestamp:
                key = f"apply{org_code}{page if page else 1}{limit if limit else 50}{timestamp}"
            else:
                key = f"apply{org_code}{page if page else 1}{limit if limit else 50}"
            cache_data = _redis.get(key=key)
            print(cache_data)
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and org_code and limit:
                res = db.select_apply_by_org_code(org_code=org_code, page=int(page), limit=int(limit))
            elif page and org_code:
                res = db.select_apply_by_org_code(org_code=org_code, page=int(page))
            elif limit and org_code:
                res = db.select_apply_by_org_code(org_code=org_code, limit=int(limit))
            elif org_code:
                res = db.select_apply_by_org_code(org_code=org_code)
            else:
                res = errorRes(status=13207, msg='参数错误')
            return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class sys_search_suggestions_view(APIView):
    """
    搜索建议，返回前50条
    请求方式：GET
    参数：KeyWords
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            keyWords = request.query_params.get("keyWords")
            return Response(db.sys_search_suggestions(keyWords=keyWords))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class like_search_suggestion_view(APIView):
    """
    搜索建议，返回前10条
    请求方式：GET
    参数：KeyWords
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            keyWords = request.query_params.get("keyWords")
            return Response(db.likeSearchSuggestion(keyWords=keyWords))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class sys_like_search_view(APIView):
    """
    模糊查询-机构用户
    请求方式：GET
    参数：searchText，[page=1,limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            timestamp = request.query_params.get("timestamp")
            cache_data = _redis.get(key=f"{searchText}{timestamp}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and searchText and limit:
                res = db.sys_like_search(searchText=searchText, page=int(page), limit=int(limit))
                return Response(res)
            elif page and searchText:
                res = db.sys_like_search(searchText=searchText, page=int(page))
                return Response(res)
            elif limit and searchText:
                res = db.sys_like_search(searchText=searchText, limit=int(limit))
                return Response(res)
            elif searchText:
                res = db.sys_like_search(searchText=searchText)
                return Response(res)
            else:
                res = db.sys_like_search(searchText='')
                return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class likeSearchView(APIView):
    """
    模糊查询
    请求方式：GET
    参数：searchText，[page=1,limit=50]
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            timestamp = request.query_params.get("timestamp")
            cache_data = _redis.get(key=f"{searchText}{timestamp}{page if page else 1}{limit if limit else 50}")
            if cache_data:  # 查询缓存是否有数据
                cache_data = bytes.decode(cache_data)
                res = ast.literal_eval(cache_data)
            elif page and searchText and limit:
                res = db.likeSearch(searchText=searchText, page=int(page), limit=int(limit))
                return Response(res)
            elif page and searchText:
                res = db.likeSearch(searchText=searchText, page=int(page))
                return Response(res)
            elif limit and searchText:
                res = db.likeSearch(searchText=searchText, limit=int(limit))
                return Response(res)
            elif searchText:
                res = db.likeSearch(searchText=searchText)
                return Response(res)
            else:
                res = db.likeSearch(searchText='')
                return Response(res)
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class likeSearchTotalView(APIView):
    """
    模糊查询总数
    请求方式：GET
    参数：searchText
    返回：
    """

    def get(self, request, *args, **kwargs):
        try:
            searchText = request.query_params.get("searchText")
            return Response(db.likeSearchTotal(searchText=searchText))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class user_details_by_idCard_view(APIView):
    """
    通过身份证查询用户详情
    请求方式：GET
    参数：idCard或者userId
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            idCard = request.query_params.get("idCard", 0)
            userId = request.query_params.get("userId", 0)
            cache_data = _redis.get(key=f"{idCard}")
            if cache_data:
                cache_data = bytes.decode(cache_data)
                return Response(ast.literal_eval(cache_data))
            return Response(db.user_details_by_idCard(idCard=idCard, userId=userId))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class userDetailsView(APIView):
    """
    通过用户ID查询用户详情
    请求方式：GET
    参数：userId
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            userId = request.query_params.get("userId")
            cache_data = _redis.get(key=f"{userId}")
            if cache_data:
                cache_data = bytes.decode(cache_data)
                return Response(ast.literal_eval(cache_data))
            return Response(db.userDetailsByUserId(userId=userId))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class userTotalView(APIView):
    """
    查询机构下用户数
    请求方式：GET
    参数：org_code
    返回：用户总数
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            return Response(db.userTotal(org_id=org_code))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)


class getUserListView(APIView):
    """
    医生登录获取该机构的用户列表
    请求方式：GET
    参数：org_code
    返回：登陆人信息
    """

    def get(self, request, *args, **kwargs):
        try:
            org_code = request.query_params.get("org_code")
            page = request.query_params.get("page")
            limit = request.query_params.get("limit")
            timestamp = request.query_params.get("timestamp")
            if page and limit and org_code:
                cache_data = _redis.get(key=f"{org_code}{page}{limit}{timestamp}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, page=page, limit=limit))
            elif page and org_code:
                cache_data = _redis.get(key=f"{org_code}{page}{50}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, page=page))
            elif limit and org_code:
                cache_data = _redis.get(key=f"{org_code}{1}{limit}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code, limit=limit))
            elif org_code:
                cache_data = _redis.get(key=f"{org_code}{1}{50}")
                if cache_data:
                    cache_data = bytes.decode(cache_data)
                    return Response(ast.literal_eval(cache_data))
                return Response(db.getUserListByOrgId(org_id=org_code))
            else:
                return Response(errorRes(status=13207, msg='参数错误'))
        except Exception as e:
            log.logger.error(msg=str(e))
            print(e)
    #
    # def post(self, request, *args, **kwargs):
    #     return Response(errorRes(status=13208, msg='接口错误'))


class sys_loginView(APIView):
    """
    公卫用户登录
    请求方式：GET
    参数：
    返回：登陆人信息
    """

    def get(self, request, *args, **kwargs):
        try:
            login = sm4.decryptData_ECB(request.query_params.get("login"))
            login = ast.literal_eval(login)
            account = login['name']
            password = login['password']
            return Response(db.sys_login(userAccount=account, userPassword=password))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))


class loginView(APIView):
    """
    用户登录
    请求方式：GET
    参数：
    返回：登陆人信息
    """

    def get(self, request, *args, **kwargs):
        try:
            login = sm4.decryptData_ECB(request.query_params.get("login"))
            login = ast.literal_eval(login)
            account = login['name']
            password = login['password']
            return Response(db.login(userAccount=account, userPassword=password))
        except Exception as e:
            log.logger.error(msg=str(e))
            return Response(errorRes(msg='请求失败，请联系管理员!'))
    #
    # def post(self, request, *args, **kwargs):
    #     return Response(errorRes(status=13208, msg='接口错误'))


class test(APIView):
    def get(self, request, *args, **kwargs):
        return Response(db.test())
