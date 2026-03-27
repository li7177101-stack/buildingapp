"""
用户信息界面
左滑返回 + 使用普通Label显示中文
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.snackbar import Snackbar
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label  # 使用普通Label
from kivy.metrics import dp
import os


class UserInfoScreen(Screen):
    """
    用户信息屏幕类
    左滑返回，使用普通Label显示中文
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_user = None
        self.dialog = None

        # 绑定触摸事件（左滑返回）
        self.touch_start_x = 0
        self.touch_start_y = 0
        self.swipe_threshold = dp(100)

        # 模拟数据
        self.user_data = {
            'username': '建筑设计师小王',
            'email': 'wang@example.com',
            'phone': '138****8888',
            'avatar': 'images/avatar.png',
            'works_count': 28,
            'favorites_count': 156,
            'followers': 89,
        }

    def on_enter(self):
        """
        进入屏幕时的回调
        """
        self.app = App.get_running_app()
        self.current_user = self.app.current_user
        self.build_ui()

    def on_touch_down(self, touch):
        """触摸按下事件 - 记录起点"""
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """触摸抬起事件 - 检测左滑手势"""
        if self.touch_start_x > 0:
            dx = touch.x - self.touch_start_x
            dy = abs(touch.y - self.touch_start_y)

            # 左滑返回
            if dx < -self.swipe_threshold and dy < dp(50):
                self.go_back()
                return True

        return super().on_touch_up(touch)

    def build_ui(self):
        """
        构建用户界面 - 使用普通Label显示中文
        """
        self.clear_widgets()

        # 主布局
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            padding=[dp(15), dp(10), dp(15), dp(15)]
        )

        # ========== 用户信息卡片（置顶） ==========
        user_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(210),
            padding=dp(15),
            spacing=dp(8),
            elevation=2,
            radius=[dp(15), dp(15), dp(15), dp(15)],
            md_bg_color=[0.95, 0.95, 0.95, 1]
        )

        # 头像和基本信息
        info_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(15),
            size_hint_y=None,
            height=dp(90)
        )

        # 头像
        avatar = Image(
            source=self.user_data['avatar'],
            size_hint=(None, None),
            size=(dp(75), dp(75)),
            allow_stretch=True,
            keep_ratio=True
        )
        info_layout.add_widget(avatar)

        # 用户名和邮箱 - 使用普通Label
        text_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_x=1
        )

        # 用户名 - 使用普通Label，确保中文显示
        username = Label(
            text=self.user_data['username'],
            font_size=dp(18),
            color=[0, 0, 0, 1],
            size_hint_y=None,
            height=dp(28),
            halign='left',
            valign='middle',
            bold=True
        )
        username.bind(size=username.setter('text_size'))
        text_layout.add_widget(username)

        # 邮箱
        email = Label(
            text=self.user_data['email'],
            font_size=dp(12),
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        email.bind(size=email.setter('text_size'))
        text_layout.add_widget(email)

        # 手机号
        phone = Label(
            text=self.user_data['phone'],
            font_size=dp(12),
            color=[0.5, 0.5, 0.5, 1],
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='middle'
        )
        phone.bind(size=phone.setter('text_size'))
        text_layout.add_widget(phone)

        info_layout.add_widget(text_layout)
        user_card.add_widget(info_layout)

        # 统计信息 - 使用普通Label
        stats_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(55),
            padding=[dp(10), dp(5), dp(10), dp(5)]
        )

        stats = [
            {'value': str(self.user_data['works_count']), 'label': '作品'},
            {'value': str(self.user_data['favorites_count']), 'label': '收藏'},
            {'value': str(self.user_data['followers']), 'label': '粉丝'},
        ]

        for stat in stats:
            stat_box = BoxLayout(
                orientation='vertical',
                spacing=dp(2),
                size_hint_x=1
            )
            value = Label(
                text=stat['value'],
                font_size=dp(20),
                color=[0.2, 0.2, 0.2, 1],
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(30),
                bold=True
            )
            value.bind(size=value.setter('text_size'))
            stat_box.add_widget(value)

            label = Label(
                text=stat['label'],
                font_size=dp(11),
                color=[0.5, 0.5, 0.5, 1],
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(20)
            )
            label.bind(size=label.setter('text_size'))
            stat_box.add_widget(label)

            stats_layout.add_widget(stat_box)

        user_card.add_widget(stats_layout)

        # 编辑资料按钮
        edit_btn = MDRectangleFlatButton(
            text="编辑资料",
            size_hint_y=None,
            height=dp(40),
            on_release=lambda x: self.show_edit_profile()
        )
        user_card.add_widget(edit_btn)

        main_layout.add_widget(user_card)

        # ========== 功能列表 ==========
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )

        menu_list = MDList(spacing=dp(5))

        # 功能菜单项 - 使用MDLabel但确保中文
        menu_items = [
            "个人信息",
            "账号安全",
            "消息通知",
            "收藏夹",
            "历史记录",
            "下载管理",
            "我的作品"
        ]

        for item in menu_items:
            # 使用OneLineListItem，它会自动处理中文
            list_item = OneLineListItem(
                text=item,
                on_release=lambda x, t=item: self.on_menu_item_click(t)
            )
            menu_list.add_widget(list_item)

        scroll_view.add_widget(menu_list)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def on_menu_item_click(self, item):
        """
        菜单项点击事件
        """
        Snackbar(text=f"{item} 功能开发中").open()

    def show_edit_profile(self):
        """
        编辑资料
        """
        Snackbar(text="编辑资料功能开发中").open()

    def go_back(self):
        """
        左滑返回主界面
        """
        self.manager.current = 'main'