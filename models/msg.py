#!/usr/bin/python3
# @Time    : 2019-10-23
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _

CONDITIONS = [
    ("focus", "被关注回复"),
    ("key", "关键字回复"),
    ("message", "收到消息回复")
]

REPLY_TYPES = [
    ("none", "不回复"),
    ("text", "文本回复"),
    ("image", "图片回复"),
    ("voice", "语音回复"),
    ("video", "视频回复"),
    ("music", "音乐回复"),
    ("news", "图文回复")
]


class WechatMessage(models.Model):
    _name = "wechat.message"

    source = fields.Char("消息来源")
    target = fields.Char("目标用户")
    create_time = fields.Datetime("发送时间")
    type = fields.Char("消息类型")
    content = fields.Char("文本消息/图片地址")
    data = fields.Text("媒体消息")


class WechatAutoReplay(models.Model):
    _name = "wechat.auto.replay"

    name = fields.Char("规则名称")
    type = fields.Selection(selection=CONDITIONS, string="触发条件")
    key = fields.Char("关键字")
    operator = fields.Selection(
        selection=[('like', "精确匹配"), ('ilike', '模糊匹配')])
    reply_type = fields.Selection(selection=REPLY_TYPES, string="回复类型")
    # [FIXME] 暂时只实现了文本回复
    text = fields.Text("回复内容")
