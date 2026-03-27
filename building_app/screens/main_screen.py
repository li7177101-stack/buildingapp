"""
主界面
包含五个功能板块，开发测试模式：免登录访问
"""

from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp


class FeatureCard(MDCard, ButtonBehavior):
    """
    功能卡片类
    优化图片显示：图片占比90%，文字占比10%
    """

    def __init__(self, feature_name='', image_source='', **kwargs):
        """
        初始化功能卡片
        """
        super().__init__(**kwargs)
        self.feature_name = feature_name
        self.image_source = image_source

        # ========== 卡片样式参数 ==========
        self.CARD_HEIGHT = dp(160)  # 卡片高度
        self.IMAGE_RATIO = 0.9  # 图片占比90%（您设置的参数）
        self.TEXT_RATIO = 0.1  # 文字占比10%
        self.PADDING_SIZE = dp(8)  # 内边距
        self.CARD_RADIUS = dp(18)  # 圆角大小
        self.CARD_ELEVATION = 2  # 阴影高度
        # ================================

        # 卡片布局
        self.orientation = 'vertical'
        self.padding = self.PADDING_SIZE
        self.radius = [self.CARD_RADIUS, ]
        self.elevation = self.CARD_ELEVATION
        self.size_hint_y = None
        self.height = self.CARD_HEIGHT
        self.md_bg_color = [1, 1, 1, 1]  # 白色背景

        # 图片区域
        img_container = BoxLayout(
            size_hint_y=self.IMAGE_RATIO,
            padding=dp(2)
        )

        self.img = Image(
            source=image_source,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        img_container.add_widget(self.img)
        self.add_widget(img_container)

        # 文字区域
        label_container = BoxLayout(
            size_hint_y=self.TEXT_RATIO,
            orientation='vertical',
            padding=[dp(2), 0, dp(2), dp(2)]
        )

        self.label = MDLabel(
            text=feature_name,
            halign='center',
            valign='middle',
            theme_text_color='Secondary',
            font_style='Subtitle1',
            shorten=True
        )
        label_container.add_widget(self.label)
        self.add_widget(label_container)


class MainScreen(Screen):
    """
    主屏幕类
    开发测试模式：所有功能免登录访问
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None

        # ========== 功能板块配置 ==========
        self.features = [
            {
                'name': '用户信息',
                'image': 'images/user_info.jpg',
                'screen': 'user_info'
            },
            {
                'name': '文生图',
                'image': 'images/text_to_img.jpg',
                'screen': 'text_to_img'
            },
            {
                'name': '图生图',
                'image': 'images/img_to_img.jpg',
                'screen': 'img_to_img'
            },
            {
                'name': '功能分析图',
                'image': 'images/analysis.jpg',
                'screen': 'analysis'
            },
            {
                'name': '规范查询',
                'image': 'images/spec_query.jpg',
                'screen': 'spec_query'
            }
        ]

        # ========== 布局参数 ==========
        self.CARD_SPACING = dp(10)  # 卡片间距
        self.SCREEN_PADDING = [dp(40), dp(8), dp(40), dp(8)]  # 您设置的左右边距40dp
        # =============================

    def on_enter(self):
        """
        进入屏幕时的回调
        """
        self.app = App.get_running_app()
        self.create_feature_cards()

    def create_feature_cards(self):
        """
        创建功能卡片
        """
        # 清空现有卡片
        self.ids.features_container.clear_widgets()

        # 创建主布局
        main_layout = BoxLayout(
            orientation='vertical',
            spacing=self.CARD_SPACING,
            padding=self.SCREEN_PADDING,
            size_hint_y=None
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # 计算总高度
        total_height = len(self.features) * (dp(160) + self.CARD_SPACING) + self.SCREEN_PADDING[1] + \
                       self.SCREEN_PADDING[3]
        main_layout.height = total_height

        # 创建卡片
        for feature in self.features:
            card = FeatureCard(
                feature_name=feature['name'],
                image_source=feature['image']
            )

            # 绑定点击事件
            card.bind(on_release=lambda x, f=feature: self.on_feature_click(f))

            main_layout.add_widget(card)

        # 添加滚动支持
        scroll_view = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        scroll_view.add_widget(main_layout)

        self.ids.features_container.add_widget(scroll_view)

    def on_feature_click(self, feature):
        """
        功能卡片点击事件
        开发测试阶段：所有功能直接可用
        """
        # 开发模式开关
        DEV_MODE = True  # True=开发模式(免登录), False=正式模式(需登录)

        if DEV_MODE:
            # ===== 开发模式：所有功能直接可用 =====
            if feature['screen'] == 'user_info':
                print(f"跳转到: {feature['screen']}")
                self.manager.current = 'user_info'
            elif feature['screen'] == 'text_to_img':
                print(f"跳转到: {feature['screen']}")
                self.manager.current = 'text_to_img'
            elif feature['screen'] == 'img_to_img':
                # 图生图 - 已开发，跳转到新界面
                print(f"跳转到: {feature['screen']}")
                self.manager.current = 'img_to_img'
            elif feature['screen'] == 'analysis':
                print("功能分析图开发中")
                self.show_developing_message()
            elif feature['screen'] == 'spec_query':
                print("规范查询功能开发中")
                self.show_developing_message()
        else:
            # ===== 正式模式：需要检查权限 =====
            if feature['screen'] in ['img_to_img', 'analysis', 'spec_query']:
                self.show_developing_message()
            else:
                if self.app.check_user_permission(feature['name']):
                    self.manager.current = feature['screen']

    def show_developing_message(self):
        """
        显示开发中提示
        """
        Snackbar(
            text="该功能正在开发中...",
            snackbar_x="10dp",
            snackbar_y="10dp",
            size_hint_x=0.7
        ).open()