# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
import logging
import traceback


_logging = logging.getLogger(__name__)


class Wechat(http.Controller):
    @http.route('/wechat/auth', auth='public')
    def index(self, **kw):
        """验证微信服务器消息"""
        try:
            signature = request.params.get("signature",None)
            timestamp = request.params.get("timestamp",None)
            echostr = request.params.get("echostr",None)
            nonce = request.params.get("nonce",None)
            token = request.env["ir.config_parameter"].sudo().get_param("wechat.token")
            check_signature(token, signature, timestamp, nonce)
        except InvalidSignatureException as ex:
            _logging.error("微信公众号服务器验证失败:{}".format(traceback.format_exc()))
        except Exception as err:
            _logging.error("验证微信公众号服务器失败:{}".format(traceback.format_exc()))
