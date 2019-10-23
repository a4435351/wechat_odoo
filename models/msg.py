#!/usr/bin/python3
# @Time    : 2019-10-23
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _


class WechatMessage(models.Model):
    _name = "wechat.message"

    source = fields.Char("消息来源")
    target = fields.Char("目标用户")
    create_time = fields.Datetime("发送时间")
    type = fields.Char("消息类型")
