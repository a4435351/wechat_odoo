#!/usr/bin/python3
# @Time    : 2019-10-23
# @Author  : Kevin Kong (kfx2007@163.com)

# 微信消息响应中心

import logging

_logger = logging.getLogger(__name__)


class WechatResponse(object):

    def __init__(self, data):
        self.data = data


    def _parse_data(self):
        """处理微信推送的消息"""
        _logger.info("微信推送消息类型：{}".format(self.data.MsgType))

    def send(self):
        """响应"""
        self._parse_data()