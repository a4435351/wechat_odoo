# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from wechatpy.utils import check_signature
from wechatpy import parse_message
from wechatpy.exceptions import InvalidSignatureException
from ..models.service import WechatResponse
import logging
import traceback


_logging = logging.getLogger(__name__)


class Wechat(http.Controller):
    @http.route('/wechat/auth', csrf=False, auth='public', method=["POST"])
    def index(self, **kw):
        """验证微信服务器消息"""
        signature = request.params.get("signature",None)
        timestamp = request.params.get("timestamp",None)
        echostr = request.params.get("echostr",None)
        nonce = request.params.get("nonce",None)
        token = request.env["ir.config_parameter"].sudo().get_param("wechat.token")
        try:
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException as ex:
            _logging.error("微信公众号服务器验证失败:{}".format(traceback.format_exc()))
        except Exception as err:
            _logging.error("验证微信公众号服务器失败:{}".format(traceback.format_exc()))
        if echostr:
            # 服务器验证请求
            return echostr
        
        ## 没有正确响应的情况下，微信服务器会推送三次消息，然后判定服务异常
        data = parse_message(request.httprequest.data.decode("utf-8"))
        _logging.info("微信服务器推送的消息：{}".format(data))
        response = WechatResponse(data)
        response.send()
