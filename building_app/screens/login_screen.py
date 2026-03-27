"""
登录界面
包含封面图片和两种登录方式
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivy.app import App  # 导入App类


class LoginScreen(Screen):
    """
    登录屏幕类
    """

    def user_login(self):
        """
        用户登录方法
        """
        # 直接获取app实例
        app = App.get_running_app()

        # 获取用户名和密码
        username = self.ids.username.text
        password = self.ids.password.text

        if username and password:
            app.login_user(username, password)
        else:
            self.show_error("请输入用户名和密码")

    def guest_login(self):
        """
        游客登录方法
        """
        # 直接获取app实例
        app = App.get_running_app()
        app.guest_login()

    def show_error(self, message):
        """
        显示错误信息
        """
        Snackbar(text=message).open()

    def go_to_register(self):
        """
        跳转到注册页面
        """
        dialog = MDDialog(
            title="注册",
            text="注册功能正在开发中...",
            buttons=[
                MDRaisedButton(
                    text="确定",
                    on_release=lambda x: dialog.dismiss()
                ),
            ],
        )
        dialog.open()