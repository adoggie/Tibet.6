# -*- coding: utf-8 -*-
import sys
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
import uuid
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.http import method_type as MT
from aliyunsdkcore.http import format_type as FT
# import const

"""
短信业务调用接口示例，版本号：v20170525

Created on 2017-06-12

"""
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:
    pass
except Exception as err:
    raise err

# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"


region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)



def send_sms(ak,secrect, business_id,phone_numbers, sign_name, template_code, template_param=None):
    acs_client = AcsClient(ak, secrect, REGION)
    smsRequest = SendSmsRequest.SendSmsRequest()

    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 数据提交方式
    # smsRequest.set_method(MT.POST)

    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    return smsResponse


if __name__ == '__main__':
    import json
    __business_id = uuid.uuid1()
    # print(__business_id)
    # params = "{\"code\":\"8888\",\"product\":\"云通信\"}"
    params = '{"code":"12323"}'

    # params = u'{"name":"wqb","code":"12345678","address":"bz","phone":"13000000000"}'
    params = json.dumps(dict(code="888999"))

    ak = "LTAI29n3aEgO7zCs"
    secret = "B03v23yB2kNURukVj3txBg6QutzO4q"

    print(send_sms(ak,secret,__business_id, "13916624477", "上海晏归", "SMS_146745088", params))
    print(send_sms(ak,secret,__business_id, "13816464618", "上海晏归", "SMS_146745088", params))
    # params = '{"code":"aguankuaihuilai"}'
    # print(send_sms(__business_id, "13381726826", "上海晏归", "SMS_146745088", params))
    # params = '{"code":"amaoshaduwa"}'
    # print(send_sms(__business_id, "13501967540", "上海晏归", "SMS_146745088", params))
    # params = '{"code":"test1"}'
    # print(send_sms(__business_id, "13816464618", "上海晏归", "SMS_146745088", params))




