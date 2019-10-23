#!/usr/bin/python3
# @Time    : 2019-10-23
# @Author  : Kevin Kong (kfx2007@163.com)

# 微信消息响应中心

from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
from odoo.http import request
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class WechatResponse(object):

    def __init__(self, data):
        self.data = data
        self._save_message()

    def _save_message(self):
        """保存消息到本地"""
        msg_obj = request.env["wechat.message"].sudo()
        msg_obj.create({
            "source": self.data.source,
            "target": self.data.target,
            "create_time": datetime.strftime(datetime.utcfromtimestamp(int(self.data.create_time)), '%Y-%m-%d %H:%M:%S'),
            "type": self.data.type
        })

    def _parse_data(self):
        """处理微信推送的消息"""
        _logger.info("微信推送消息类型：{}".format(self.data.type))
        return TextReply(content="您好，公众号正在建设中，感谢关注", message=self.data).render()

    def send(self):
        """响应"""
        data = self._parse_data()
        _logger.debug("响应微信消息：{}".format(data))
        return data
