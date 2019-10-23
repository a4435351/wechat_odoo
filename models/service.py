#!/usr/bin/python3
# @Time    : 2019-10-23
# @Author  : Kevin Kong (kfx2007@163.com)

# 微信消息响应中心

from wechatpy.messages import TextMessage
from wechatpy.replies import TextReply
import logging

_logger = logging.getLogger(__name__)


class WechatResponse(object):

    def __init__(self, data):
        self.data = data

    def _parse_data(self):
        """处理微信推送的消息"""
        _logger.info("微信推送消息类型：{}".format(self.data.type))
        return TextReply(content="您好，公众号正在建设中，感谢关注", message=self.data).render()

    def send(self):
        """响应"""
        data = self._parse_data()
        _logger.info("响应微信消息：{}".format(data))
        return data
