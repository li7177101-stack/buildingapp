"""
图生图界面 - 与文生图布局一致
图片占满屏幕宽度，单张大图显示，无阴影
"""

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage, Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
import threading
import time
import requests
import json
import base64
import random
import os
import tempfile


class ImgToImgScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_image = None
        self.generated_images = []
        self.image_history = []
        self.prompt_input = None
        self.is_generating = False
        self.uploaded_image = None
        self.uploaded_image_data = None
        self.images_grid = None

        # ===== GrsAI配置 =====
        self.BASE_URL = "https://grsai.dakka.com.cn"
        self.API_KEY = "sk-9073d509c4344f428e4ab6c48af41083"  # 请替换为您的API Key
        self.MODEL_NAME = "nano-banana"
        self.ASPECT_RATIO = "1:1"

        self.BOTTOM_HEIGHT = 180
        self.touch_start_x = 0
        self.touch_start_y = 0
        self.swipe_threshold = 100

    def on_enter(self):
        self.app = App.get_running_app()
        self.build_ui()

    def on_touch_down(self, touch):
        self.touch_start_x = touch.x
        self.touch_start_y = touch.y
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.touch_start_x > 0:
            dx = touch.x - self.touch_start_x
            dy = abs(touch.y - self.touch_start_y)
            if dx < -self.swipe_threshold and dy < 50:
                self.go_back()
                return True
        return super().on_touch_up(touch)

    def build_ui(self):
        """构建界面 - 与文生图一致"""
        self.clear_widgets()
        main = BoxLayout(orientation='vertical')

        # 图片区域
        self.image_area = BoxLayout(size_hint_y=1, orientation='vertical')
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=False)
        self.image_container = BoxLayout(
            size_hint_y=None,
            height=Window.height - self.BOTTOM_HEIGHT - 10,
            orientation='vertical',
            padding=[0, 0, 0, 0]
        )

        # 如果没有生成图片，显示上传区域
        if len(self.generated_images) == 0:
            self._show_upload_area()
        else:
            self._update_display()

        self.scroll.add_widget(self.image_container)
        self.image_area.add_widget(self.scroll)
        main.add_widget(self.image_area)

        # ========== 底部输入区域 ==========
        bottom = BoxLayout(orientation='vertical', size_hint_y=None, height=self.BOTTOM_HEIGHT,
                           spacing=5, padding=[10, 5, 10, 10])

        # 输入框
        self.prompt_input = TextInput(
            hint_text="输入修改描述...",
            size_hint_y=None,
            height=dp(52),
            multiline=False,
            font_size='16sp',
            padding=[dp(10), dp(10), dp(10), dp(10)],
            background_color=[0.95, 0.95, 0.95, 1],
            foreground_color=[0, 0, 0, 1],
            cursor_color=[0.2, 0.6, 0.9, 1],
            cursor_width=dp(2)
        )
        bottom.add_widget(self.prompt_input)

        # 按钮行
        btn_row = BoxLayout(
            size_hint_y=None,
            height=48,
            spacing=8,
            size_hint_x=None,
            width=300,
            pos_hint={'center_x': 0.5}
        )

        generate_btn = MDRaisedButton(
            text="✨ 生成",
            size_hint_x=0.25,
            on_release=self.generate_image
        )

        history_btn = MDFlatButton(
            text="📋 历史",
            size_hint_x=0.25,
            on_release=self.show_history
        )

        save_btn = MDFlatButton(
            text="💾 保存",
            size_hint_x=0.25,
            on_release=lambda x: self.save_image()
        )

        share_btn = MDFlatButton(
            text="📤 分享",
            size_hint_x=0.25,
            on_release=lambda x: self.share_image()
        )

        btn_row.add_widget(generate_btn)
        btn_row.add_widget(history_btn)
        btn_row.add_widget(save_btn)
        btn_row.add_widget(share_btn)
        bottom.add_widget(btn_row)

        # 快捷提示
        tips_row = BoxLayout(size_hint_y=None, height=30, spacing=2)
        tips = ["现代", "中式", "简约", "细节", "夜景", "日景"]
        for tip in tips:
            tip_btn = Button(
                text=tip, size_hint_x=1 / len(tips),
                background_color=[0.3, 0.3, 0.3, 1],
                color=[1, 1, 1, 1],
                on_release=lambda x, t=tip: self.use_tip(t)
            )
            tips_row.add_widget(tip_btn)

        bottom.add_widget(tips_row)
        main.add_widget(bottom)
        self.add_widget(main)

    def _show_upload_area(self):
        """显示图片上传区域 - 占满整个图片区域"""
        # 计算图片区域高度
        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        upload_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=image_area_height,
            padding=[20, 20, 20, 20],
            spacing=10
        )

        upload_btn = Button(
            text="📸 点击上传图片\n\n支持 JPG、PNG\n最大 10MB",
            size_hint_y=0.6,
            background_color=[0.9, 0.9, 0.9, 1],
            color=[0.2, 0.2, 0.2, 1],
            font_size='18sp',
            on_release=self.select_image
        )
        upload_container.add_widget(upload_btn)

        tip_label = MDLabel(
            text="上传图片后，输入描述文字\nAI将根据您的图片和描述生成新图片",
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=0.2
        )
        upload_container.add_widget(tip_label)

        example_label = MDLabel(
            text="示例：\n• 改成现代风格\n• 增加玻璃幕墙\n• 变成夜景",
            halign='center',
            theme_text_color='Secondary',
            size_hint_y=0.2
        )
        upload_container.add_widget(example_label)

        self.image_container.add_widget(upload_container)

    def _show_uploaded_image(self, image_path):
        """显示已上传的图片 - 占满整个区域"""
        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        self.image_container.clear_widgets()

        # 创建单列网格
        grid = GridLayout(
            cols=1,
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        # 创建图片卡片
        card = MDCard(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=None,
            height=image_area_height - 5,
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=0,
            elevation=0
        )

        img = Image(
            source=image_path,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        card.add_widget(img)

        grid.add_widget(card)

        # 添加重新上传按钮
        reupload_btn = MDFlatButton(
            text="🔄 重新上传",
            size_hint_y=None,
            height=40,
            on_release=self.select_image
        )
        grid.add_widget(reupload_btn)

        self.image_container.add_widget(grid)

    def select_image(self, *args):
        """选择图片"""
        try:
            from plyer import filechooser

            filechooser.open_file(
                on_selection=self._on_image_selected,
                filters=[["Images", "*.jpg", "*.jpeg", "*.png"]]
            )
        except ImportError:
            Snackbar(text="请手动将图片放入 images/ 目录后重试").open()

    def _on_image_selected(self, selection):
        """图片选择回调"""
        if selection:
            image_path = selection[0]
            self.uploaded_image = image_path
            self._load_image_to_base64(image_path)
            self._show_uploaded_image(image_path)
            Snackbar(text="✅ 图片已上传").open()

    def _load_image_to_base64(self, image_path):
        """将图片转换为base64"""
        try:
            with open(image_path, 'rb') as f:
                self.uploaded_image_data = base64.b64encode(f.read()).decode()
            print(f"✅ 图片已加载，大小: {len(self.uploaded_image_data)} 字节")
        except Exception as e:
            print(f"❌ 图片加载失败: {e}")
            self.uploaded_image_data = None

    def use_tip(self, tip):
        if self.prompt_input:
            current = self.prompt_input.text
            self.prompt_input.text = current + " " + tip if current else tip

    def generate_image(self, *args):
        if not self.uploaded_image_data:
            Snackbar(text="请先上传图片").open()
            return

        prompt = self.prompt_input.text.strip() if self.prompt_input else ""
        if not prompt:
            Snackbar(text="请输入修改描述").open()
            return

        if self.is_generating:
            Snackbar(text="正在生成中，请稍候...").open()
            return

        self.is_generating = True
        Snackbar(text=f"🎨 正在处理: {prompt[:30]}...").open()

        threading.Thread(target=self._call_img2img_api, args=(prompt,), daemon=True).start()

    def _call_img2img_api(self, prompt):
        """调用图生图API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_KEY}"
            }

            payload = {
                "model": self.MODEL_NAME,
                "prompt": prompt,
                "image": self.uploaded_image_data,
                "strength": 0.7,
                "aspectRatio": self.ASPECT_RATIO,
                "webHook": "-1"
            }

            print(f"📤 提交图生图任务...")
            print(f"📤 提示词: {prompt[:50]}...")
            print(f"📤 图片大小: {len(self.uploaded_image_data)} 字节")

            submit_url = f"{self.BASE_URL}/v1/draw/nano-banana"
            response = requests.post(submit_url, json=payload, headers=headers, timeout=60)

            if response.status_code != 200:
                Clock.schedule_once(lambda dt: self._show_error(f"API错误: {response.status_code}"))
                return

            task_data = response.json()

            if task_data.get('code') != 0:
                error_msg = task_data.get('msg', '未知错误')
                Clock.schedule_once(lambda dt: self._show_error(f"API错误: {error_msg}"))
                return

            task_id = task_data.get('data', {}).get('id')
            if not task_id:
                Clock.schedule_once(lambda dt: self._show_error("获取任务ID失败"))
                return

            print(f"✅ 任务ID: {task_id}")

            result_url = f"{self.BASE_URL}/v1/draw/result"
            max_attempts = 60
            wait_time = 3

            for attempt in range(max_attempts):
                time.sleep(wait_time)

                result_response = requests.post(
                    result_url,
                    json={"id": task_id},
                    headers=headers,
                    timeout=30
                )

                if result_response.status_code != 200:
                    continue

                result = result_response.json()

                if attempt % 5 == 0:
                    print(f"📦 第{attempt + 1}次查询: 进度 {result.get('data', {}).get('progress', 0)}%")

                if result.get('code') == 0:
                    data = result.get('data', {})
                    status = data.get('status')

                    if status == 'succeeded':
                        results = data.get('results', [])
                        if results and len(results) > 0:
                            image_url = results[0].get('url')
                            if image_url:
                                print(f"✅ 图生图成功！")
                                Clock.schedule_once(
                                    lambda dt, u=image_url, p=prompt: self._add_generated_image(u, p)
                                )
                                return

                    elif status == 'failed':
                        Clock.schedule_once(lambda dt: self._show_error("生成失败"))
                        return

            Clock.schedule_once(lambda dt: self._show_error("生成超时"))

        except Exception as e:
            print(f"❌ 异常: {e}")
            Clock.schedule_once(lambda dt: self._show_error("网络错误"))
        finally:
            self.is_generating = False

    def _add_generated_image(self, image_url, prompt):
        """添加生成的图片"""
        Clock.schedule_once(lambda dt: self._show_loading(), 0)

        def download_image():
            max_retries = 3
            for retry in range(max_retries):
                try:
                    response = requests.get(image_url, timeout=60)
                    if response.status_code == 200:
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, f"img2img_{int(time.time())}.png")
                        with open(temp_path, 'wb') as f:
                            f.write(response.content)
                        Clock.schedule_once(lambda dt: self._display_image(temp_path, prompt))
                        return
                except requests.exceptions.Timeout:
                    print(f"⏰ 下载超时 (尝试 {retry + 1}/{max_retries})")
                    if retry == max_retries - 1:
                        Clock.schedule_once(lambda dt: self._display_image_from_url(image_url, prompt))
                        return
                    time.sleep(3)
                except Exception as e:
                    print(f"❌ 下载失败: {e}")
                    if retry == max_retries - 1:
                        Clock.schedule_once(lambda dt: self._display_image_from_url(image_url, prompt))
                        return
                    time.sleep(3)

        threading.Thread(target=download_image, daemon=True).start()

    def _show_loading(self):
        """显示加载中"""
        self.image_container.clear_widgets()

        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        loading_card = MDCard(
            orientation='vertical',
            size_hint=(1, 1),
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=20,
            elevation=0
        )
        loading_label = MDLabel(
            text="⏳ 正在生成图片...",
            halign='center',
            valign='middle'
        )
        loading_card.add_widget(loading_label)
        self.image_container.add_widget(loading_card)

    def _display_image(self, image_path, prompt):
        """显示图片 - 占满整个上半部分，与文生图一致"""
        self.image_container.clear_widgets()

        # 计算图片区域可用高度
        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        # 创建单列网格，让图片占满整个宽度
        grid = GridLayout(
            cols=1,
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        # 创建图片卡片 - 几乎占满整个图片区域
        card = MDCard(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=None,
            height=image_area_height - 5,
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=0,
            elevation=0
        )

        img = Image(
            source=image_path,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        card.add_widget(img)

        grid.add_widget(card)
        self.image_container.add_widget(grid)
        self.images_grid = grid
        self.generated_images.append(card)
        self.image_history.append({
            'prompt': prompt,
            'image': image_path,
            'color': [1, 1, 1, 1]
        })

        self.current_image = None
        self.is_generating = False
        Snackbar(text=f"✅ 生成完成!").open()

    def _display_image_from_url(self, image_url, prompt):
        """直接使用URL显示图片"""
        self.image_container.clear_widgets()

        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        grid = GridLayout(
            cols=1,
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        card = MDCard(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=None,
            height=image_area_height - 5,
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=0,
            elevation=0
        )

        img = AsyncImage(
            source=image_url,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        card.add_widget(img)

        grid.add_widget(card)
        self.image_container.add_widget(grid)
        self.images_grid = grid
        self.generated_images.append(card)
        self.image_history.append({
            'prompt': prompt,
            'image': image_url,
            'color': [1, 1, 1, 1]
        })

        self.current_image = None
        self.is_generating = False
        Snackbar(text=f"✅ 生成完成!").open()

    def _update_display(self):
        """更新显示"""
        self.image_container.clear_widgets()

        if len(self.generated_images) > 0:
            image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

            grid = GridLayout(
                cols=1,
                spacing=0,
                padding=[0, 0, 0, 0],
                size_hint_y=None
            )
            grid.bind(minimum_height=grid.setter('height'))

            for card in self.generated_images:
                card.size_hint_x = 1
                card.height = image_area_height - 5
                grid.add_widget(card)

            self.image_container.add_widget(grid)
            self.images_grid = grid
        else:
            self._show_upload_area()

    def save_image(self):
        if len(self.generated_images) == 0:
            Snackbar(text="没有可保存的图片").open()
            return

        try:
            save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "BuildingApp")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"img2img_{timestamp}.png"
            filepath = os.path.join(save_dir, filename)

            current_image = self.image_history[-1]['image'] if self.image_history else None
            if current_image and os.path.exists(current_image):
                import shutil
                shutil.copy(current_image, filepath)
                Snackbar(text=f"✅ 已保存").open()
            else:
                Snackbar(text="无法获取图片数据").open()
        except Exception as e:
            print(f"保存失败: {e}")
            Snackbar(text="❌ 保存失败").open()

    def share_image(self):
        if len(self.generated_images) == 0:
            Snackbar(text="没有可分享的图片").open()
            return

        try:
            from kivy.core.clipboard import Clipboard
            current_image = self.image_history[-1]['image'] if self.image_history else None
            if current_image:
                Clipboard.copy(current_image)
                Snackbar(text="📋 图片路径已复制").open()
        except:
            Snackbar(text="分享功能开发中").open()

    def show_history(self, *args):
        if len(self.image_history) == 0:
            Snackbar(text="暂无历史记录").open()
            return

        idx = random.randint(0, len(self.image_history) - 1)
        item = self.image_history[idx]

        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        # 创建单列网格容器
        grid = GridLayout(
            cols=1,
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        # 创建临时卡片
        temp_card = MDCard(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=None,
            height=image_area_height - 5,
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=0,
            elevation=0
        )
        temp_img = Image(
            source=item['image'],
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        temp_card.add_widget(temp_img)

        grid.add_widget(temp_card)

        self.image_container.clear_widgets()
        self.image_container.add_widget(grid)

        Clock.schedule_once(lambda dt: self._restore_display(), 3)
        Snackbar(text=f"📋 历史: {item['prompt'][:20]}...").open()

    def _restore_display(self):
        """恢复显示"""
        self.image_container.clear_widgets()
        if len(self.generated_images) > 0:
            self._update_display()
        else:
            self._show_upload_area()

    def _show_error(self, message):
        Snackbar(text=f"❌ {message}").open()
        self.is_generating = False

    def go_back(self):
        self.manager.current = 'main'