"""
建筑意向图APP主入口文件
基于Kivy和KivyMD开发
支持Python 3.9
"""

import os
import sys
from kivy.config import Config

# ===== 输入法优化配置 =====
os.environ['KIVY_IME'] = '1'
os.environ['KIVY_TEXT'] = 'sdl2'
# ========================

from kivy.config import Config
Config.set('kivy', 'desktop', 1)
Config.set('kivy', 'keyboard_mode', 'auto')  # 使用系统键盘

# 配置窗口大小（用于调试，打包时会自动适应手机）
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.core.image import Image as CoreImage
from kivy.utils import get_color_from_hex

# 导入自定义屏幕类
from building_app.screens.login_screen import LoginScreen
from building_app.screens.main_screen import MainScreen
from building_app.screens.user_info_screen import UserInfoScreen
from building_app.screens.text_to_img_screen import TextToImageScreen
from building_app.screens.img_to_img_screen import ImgToImgScreen


# 注册中文字体
from kivy.utils import platform


def register_chinese_font():
    """注册中文字体（跨平台兼容）"""
    # iOS 和 Android 系统自带中文字体，Kivy 会自动处理
    if platform in ('ios', 'android'):
        # 设置默认字体为中文字体
        from kivy.core.text import LabelBase
        LabelBase.register(name='Roboto', fn_regular='')
        # Kivy 会自动使用系统字体，无需额外操作
        return

    # Windows/Linux 开发环境：尝试加载本地中文字体
    import os
    font_paths = [
        'C:\\Windows\\Fonts\\msyh.ttc',
        'C:\\Windows\\Fonts\\simhei.ttf',
        'C:\\Windows\\Fonts\\simsun.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',  # Linux
        '/System/Library/Fonts/PingFang.ttc',  # macOS
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                from kivy.core.text import LabelBase
                LabelBase.register(name='Chinese', fn_regular=font_path)
                # 设置为默认字体
                LabelBase.register(name='Roboto', fn_regular=font_path)
                print(f"已加载中文字体: {font_path}")
                return
            except:
                continue

    print("未找到中文字体，将使用系统默认字体")


class BuildingApp(MDApp):
    """
    主应用类
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "建筑意向图生成器"
        self.current_user = {
            'is_logged_in': False,
            'user_type': 'guest',
            'username': '游客'
        }

    def build(self):
        """
        构建应用界面
        """
        # ===== 配置输入法支持 =====
        from kivy.config import Config
        Config.set('kivy', 'desktop', 1)  # 启用桌面模式
        Config.set('input', 'mouse', 'mouse,disable_on_activity')  # 配置鼠标输入
        # =========================

        # 设置主题
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # 注册中文字体
        register_chinese_font()

        # 加载KV文件
        kv_files = [
            'building_app/screens/login_screen.kv',
            'building_app/screens/main_screen.kv',
            'building_app/screens/user_info_screen.kv',
            'building_app/screens/text_to_img_screen.kv',
            'building_app/screens/img_to_img_screen.kv',  # 新增
        ]

        for kv_file in kv_files:
            if os.path.exists(kv_file):
                Builder.load_file(kv_file)

        # 创建屏幕管理器
        self.sm = ScreenManager(transition=SlideTransition())

        # 添加屏幕
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(UserInfoScreen(name='user_info'))
        self.sm.add_widget(TextToImageScreen(name='text_to_img'))
        self.sm.add_widget(ImgToImgScreen(name='img_to_img'))  # 新增

        return self.sm

    def login_user(self, username, password):
        """
        用户登录
        """
        self.current_user['is_logged_in'] = True
        self.current_user['user_type'] = 'user'
        self.current_user['username'] = username
        self.sm.current = 'main'
        return True

    def guest_login(self):
        """
        游客登录
        """
        self.current_user['is_logged_in'] = False
        self.current_user['user_type'] = 'guest'
        self.sm.current = 'main'

    def check_user_permission(self, feature):
        """
        检查用户权限
        """
        if self.current_user['user_type'] == 'guest':
            from kivymd.uix.dialog import MDDialog
            from kivymd.uix.button import MDFlatButton

            dialog = MDDialog(
                title="需要注册",
                text="该功能需要注册登录后才能使用，是否立即注册？",
                buttons=[
                    MDFlatButton(
                        text="取消",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="去注册",
                        on_release=lambda x: self.go_to_register(dialog)
                    ),
                ],
            )
            dialog.open()
            return False
        return True

    def go_to_register(self, dialog):
        """
        跳转到注册页面
        """
        dialog.dismiss()
        self.sm.current = 'login'

    def on_start(self):
        """
        应用启动时的回调
        """
        super().on_start()

    def on_pause(self):
        """
        应用暂停时的回调（Android）
        """
        return True

    def on_resume(self):
        """
        应用恢复时的回调（Android）
        """
        pass


if __name__ == '__main__':
    BuildingApp().run()
