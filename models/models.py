#!/usr/bin/python3
# @Time    : 2019-10-21
# @Author  : Kevin Kong (kfx2007@163.com)

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessDenied
from wechatpy import WeChatClient
import logging
import traceback


_logger = logging.getLogger(__name__)

MENU_TYPES = [
    ('click', "单击事件"),
    ('view', "URL跳转"),
    ("scancode_push", "扫码推送结果"),
    ("scancode_waitmsg", "扫码接收消息"),
    ("pic_sysphoto", "拍照"),
    ("pic_photo_or_album", "拍照或者从相册中选择"),
    ("pic_weixin", "从微信相册中选择"),
    ("location_select", "选取微信地理位置"),
    ("media_id", "下发多媒体消息"),
    ("view_limited", "跳转图文消息URL"),
    ("miniprogram", "小程序")
]

CLICK_TYPES = ("click", "scancode_push", "scancode_waitmsg",
               "pic_sysphoto", "pic_photo_or_album", "pic_weixin", "location_select")
MEDIA_TYPES = ("media_id", "view_limited")
URL_TYPES = ("view", "miniprogram")


class wechat_menu(models.Model):
    """
    公众号菜单配置
    自定义菜单最多包括3个一级菜单，每个一级菜单最多包含5个二级菜单
    一级菜单最多4个汉字，二级菜单最多7个汉字，多出来的部分将会以“...”代替
    """

    _name = "wechat.menu"
    _parent_store = True

    name = fields.Char("菜单", required=True, size=60)
    parent_path = fields.Char(index=True)
    type = fields.Selection(string="菜单类型", selection=MENU_TYPES, required=True)
    level = fields.Selection(
        selection=[("1", "一级菜单"), ("2", "二级菜单")], string="菜单级别", required=True)
    parent_id = fields.Many2one("wechat.menu", string="上级菜单")
    key = fields.Char("菜单KEY值", size=128)
    url = fields.Char("URL", size=1024)
    media_id = fields.Char("MEIDA_ID")
    appid = fields.Char("小程序APPID")
    pagepath = fields.Char("小程序页面路径")

    def _get_menu_data(self):
        """获取菜单数据"""
        menus = self.search([('level', '=', '1')])
        data = {
            "button": []
        }
        for menu in menus:
            child_menus = self.search(
                [('level', '=', '2'), ('parent_id', '=', menu.id)])
            if not child_menus:
                # 无子菜单的一级菜单
                if self.type in CLICK_TYPES:
                    data["button"].append({
                        "type": self.type,
                        "name": self.name,
                        "key": self.key
                    })
                if self.type in MEDIA_TYPES:
                    data["button"].append({
                        "type": self.type,
                        "name": self.name,
                        "media_id": self.media_id
                    })
                if self.type in URL_TYPES:
                    m = {
                        "type": self.type,
                        "name": self.name,
                        "url": self.url
                    }
                    if self.type == "miniprogram":
                        m["appid"] = self.appid
                        m["pagepath"] = self.pagepath

                    data["button"].append(m)
            else:
                # 有子菜单
                menu_data = {
                    "name": self.name,
                    "sub_button": []
                }
                # 遍历子菜单
                for sub in child_menus:
                    if sub.type in CLICK_TYPES:
                        menu_data["sub_button"].append({
                            "type": sub.type,
                            "name": sub.name,
                            "key": sub.key
                        })
                    if sub.type in MEDIA_TYPES:
                        menu_data["sub_button"].append({
                            "type": sub.type,
                            "name": sub.name,
                            "media_id": sub.media_id
                        })
                    if sub.type in URL_TYPES:
                        m = {
                            "type": sub.type,
                            "name": sub.name,
                            "url": sub.url
                        }
                        if sub.type == "miniprogram":
                            m["appid"] = sub.appid
                            m["pagepath"] = sub.pagepath

                        menu_data["sub_button"].append(m)
                data["button"].append(menu_data)
        return data

    def __create_wechat_menu(self, data):
        """创建微信菜单"""
        try:
            appid = self.env["ir.config_parameter"].sudo(
            ).get_param("wechat.appid")
            appsecret = self.env["ir.config_parameter"].sudo(
            ).get_param("wechat.secret")
            client = WeChatClient(appid, appsecret)
            client.menu.create(data)
        except Exception as err:
            _logger.error("创建微信公众号菜单异常：{}".format(traceback.format_exc()))

    def __update_wechat_menu(self, data):
        """更新微信菜单"""
        try:
            appid = self.env["ir.config_parameter"].sudo(
            ).get_param("wechat.appid")
            appsecret = self.env["ir.config_parameter"].sudo(
            ).get_param("wechat.secret")
            client = WeChatClient(appid, appsecret)
            client.menu.update(data)
        except Exception as err:
            _logger.error("更新微信公众号菜单异常：{}".format(traceback.format_exc()))
            raise AccessDenied(err)

    def _create_wechat_menu(self):
        """创建微信自定义菜单"""
        self.__create_wechat_menu(self._get_menu_data())

    def _update_wechat_menu(self):
        """更新微信自定义菜单"""
        self.__update_wechat_menu(self._get_menu_data())

    @api.model
    def create(self, value):
        """
        创建菜单
        一级菜单最多3个，二级最多5个
        """
        if value["level"] == "1":
            menus = self.search([('level', '=', "1")])
            if len(menus) >= 3:
                raise UserError("一级菜单最多3个")
        if value["level"] == "2":
            menus = self.search(
                [('level', '=', 2), ('parent_id', '=', value["parent_id"])])
            if len(menus) >= 5:
                raise UserError("二级菜单最多5个")
        res = super(wechat_menu, self).create(value)
        self._create_wechat_menu()
        return res

    @api.multi
    def write(self, value):
        """
        编辑菜单
        """
        res = super(wechat_menu, self).write(value)
        if self.level == "1":
            menus = self.search([('level', '=', '1')])
            if len(menus) >= 3:
                raise UserError("一级菜单最多3个")
        if self.level == "2":
            menus = self.search(
                [('level', '=', '2'), ('parent_id', '=', self.parent_id.id)])
            if len(menus) >= 5:
                raise UserError("二级菜单最多5个")
        self._update_wechat_menu()
        return res

    @api.multi
    def unlink(self):
        """
        删除菜单
        仅当菜单数量为0时删除自定义菜单
        """
        res = super(wechat_menu, self).unlink()
        menus = self.search([])
        if menus:
            try:
                appid = self.env["ir.config_parameter"].sudo(
                ).get_param("wechat.appid")
                appsecret = self.env["ir.config_parameter"].sudo(
                ).get_param("wechat.secret")
                client = WeChatClient(appid, appsecret)
                client.menu.delete()
            except Exception as err:
                _logger.error("删除微信公众号自定义菜单异常：{}".format(
                    traceback.format_exc()))
                raise AccessDenied(err)
        else:
            # 更新菜单
            self._update_wechat_menu()
        return res
