"""
文生图界面 - 优化版
图片占满屏幕宽度，无阴影
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


class TextToImageScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_image = None
        self.generated_images = []
        self.image_history = []
        self.prompt_input = None
        self.is_generating = False
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
        """构建界面"""
        self.clear_widgets()
        main = BoxLayout(orientation='vertical')

        # 图片区域
        self.image_area = BoxLayout(size_hint_y=1, orientation='vertical')
        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False, do_scroll_y=False)
        self.image_container = BoxLayout(
            size_hint_y=None,
            height=Window.height - self.BOTTOM_HEIGHT - 10,
            orientation='vertical',
            padding=[0, 0, 0, 0]  # 左右padding为0，占满宽度
        )

        self._update_display()
        self.scroll.add_widget(self.image_container)
        self.image_area.add_widget(self.scroll)
        main.add_widget(self.image_area)

        # ========== 底部输入区域 ==========
        bottom = BoxLayout(orientation='vertical', size_hint_y=None, height=self.BOTTOM_HEIGHT,
                           spacing=5, padding=[10, 5, 10, 10])

        # 输入框
        self.prompt_input = TextInput(
            hint_text="输入建筑意向描述...",
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
        tips = ["现代", "中式", "简约", "别墅", "办公楼"]
        for tip in tips:
            tip_btn = Button(
                text=tip, size_hint_x=0.2,
                background_color=[0.3, 0.3, 0.3, 1],
                color=[1, 1, 1, 1],
                on_release=lambda x, t=tip: self.use_tip(t)
            )
            tips_row.add_widget(tip_btn)

        bottom.add_widget(tips_row)
        main.add_widget(bottom)
        self.add_widget(main)

    def use_tip(self, tip):
        if self.prompt_input:
            current = self.prompt_input.text
            self.prompt_input.text = current + " " + tip if current else tip

    def generate_image(self, *args):
        prompt = self.prompt_input.text.strip() if self.prompt_input else ""
        if not prompt:
            Snackbar(text="请输入描述").open()
            return

        if self.is_generating:
            Snackbar(text="正在生成中，请稍候...").open()
            return

        self.is_generating = True
        Snackbar(text=f"🎨 正在生成: {prompt[:30]}...").open()

        threading.Thread(target=self._call_grsai_api, args=(prompt,), daemon=True).start()

    def _call_grsai_api(self, prompt):
        """调用GrsAI API - 添加详细调试"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_KEY}"
            }

            payload = {
                "model": self.MODEL_NAME,
                "prompt": prompt,
                "aspectRatio": self.ASPECT_RATIO,
                "webHook": "-1"
            }

            print(f"📤 提交任务: {prompt[:50]}...")
            print(f"📤 API Key: {self.API_KEY[:10]}...")
            print(f"📤 URL: {self.BASE_URL}/v1/draw/nano-banana")

            submit_url = f"{self.BASE_URL}/v1/draw/nano-banana"

            print("📤 发送请求...")
            response = requests.post(submit_url, json=payload, headers=headers, timeout=60)

            print(f"📥 状态码: {response.status_code}")
            print(f"📥 响应内容: {response.text[:500]}")

            if response.status_code != 200:
                print(f"❌ 提交失败: {response.status_code}")
                Clock.schedule_once(lambda dt: self._show_error(f"API错误: {response.status_code}"))
                return

            task_data = response.json()
            print(f"📦 解析成功: {task_data}")

            if task_data.get('code') != 0:
                error_msg = task_data.get('msg', '未知错误')
                print(f"❌ API错误: {error_msg}")
                Clock.schedule_once(lambda dt: self._show_error(f"API错误: {error_msg}"))
                return

            task_id = task_data.get('data', {}).get('id')
            if not task_id:
                print(f"❌ 无法获取任务ID")
                Clock.schedule_once(lambda dt: self._show_error("获取任务ID失败"))
                return

            print(f"✅ 任务ID: {task_id}")

            # 轮询结果
            result_url = f"{self.BASE_URL}/v1/draw/result"
            max_attempts = 60
            wait_time = 3

            for attempt in range(max_attempts):
                print(f"⏳ 轮询第 {attempt + 1}/{max_attempts} 次")
                time.sleep(wait_time)

                result_response = requests.post(
                    result_url,
                    json={"id": task_id},
                    headers=headers,
                    timeout=30
                )

                if result_response.status_code != 200:
                    print(f"⚠️ 轮询响应码: {result_response.status_code}")
                    continue

                result = result_response.json()
                print(f"📦 轮询结果: 进度 {result.get('data', {}).get('progress', 0)}%")

                if result.get('code') == 0:
                    data = result.get('data', {})
                    status = data.get('status')

                    if status == 'succeeded':
                        results = data.get('results', [])
                        if results and len(results) > 0:
                            image_url = results[0].get('url')
                            if image_url:
                                print(f"✅ 生成成功！")
                                Clock.schedule_once(
                                    lambda dt, u=image_url, p=prompt: self._add_generated_image(u, p)
                                )
                                return

                    elif status == 'failed':
                        failure_reason = data.get('failure_reason', '未知错误')
                        print(f"❌ 生成失败: {failure_reason}")
                        Clock.schedule_once(lambda dt: self._show_error("生成失败"))
                        return

            print("⏰ 轮询超时")
            Clock.schedule_once(lambda dt: self._show_error("生成超时"))

        except requests.exceptions.Timeout:
            print("⏰ 请求超时")
            Clock.schedule_once(lambda dt: self._show_error("请求超时，请重试"))
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接错误")
            Clock.schedule_once(lambda dt: self._show_error("网络连接失败"))
        except Exception as e:
            print(f"❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            Clock.schedule_once(lambda dt: self._show_error(f"网络错误"))
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
                        temp_path = os.path.join(temp_dir, f"text2img_{int(time.time())}.png")
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
        loading_card = MDCard(
            orientation='vertical',
            size_hint=(1, 1),
            md_bg_color=[1, 1, 1, 1],
            radius=[0, 0, 0, 0],
            padding=20,
            elevation=0
        )
        loading_label = MDLabel(
            text="⏳ 正在加载图片...",
            halign='center',
            valign='middle'
        )
        loading_card.add_widget(loading_label)
        self.image_container.add_widget(loading_card)

    def _display_image(self, image_path, prompt):
        """显示图片 - 图片区域最大化，占满整个上半部分"""
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
            height=image_area_height - 5,  # 留一点边距
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

        grid = GridLayout(
            cols=2,
            spacing=2,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        card = MDCard(
            orientation='vertical',
            size_hint_x=0.5,
            size_hint_y=None,
            height=180,
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

    def save_image(self):
        if len(self.generated_images) == 0:
            Snackbar(text="没有可保存的图片").open()
            return

        try:
            save_dir = os.path.join(os.path.expanduser("~"), "Pictures", "BuildingApp")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"text2img_{timestamp}.png"
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

    def _show_error(self, message):
        Snackbar(text=f"❌ {message}").open()
        self.is_generating = False

    def _create_empty_button(self):
        """创建空状态按钮 - 占满整个区域"""
        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10
        return Button(
            text="🎨 输入描述，点击生成\n\n示例：\n现代别墅 | 中式庭院 | 办公楼",
            size_hint=(1, 1),
            background_color=[0.95, 0.95, 0.95, 1],
            color=[0.2, 0.2, 0.2, 1],
            font_size='18sp',
            bold=True
        )

    def _update_display(self):
        """更新显示"""
        self.image_container.clear_widgets()

        if len(self.generated_images) > 0:
            # 有生成图片时，使用网格布局
            grid = GridLayout(
                cols=2,
                spacing=2,
                padding=[0, 0, 0, 0],
                size_hint_y=None
            )
            grid.bind(minimum_height=grid.setter('height'))

            for card in self.generated_images:
                card.size_hint_x = 0.5
                grid.add_widget(card)

            self.image_container.add_widget(grid)
            self.images_grid = grid
        else:
            # 无图片时显示空状态
            empty_btn = self._create_empty_button()
            self.image_container.add_widget(empty_btn)

    def show_history(self, *args):
        if len(self.image_history) == 0:
            Snackbar(text="暂无历史记录").open()
            return

        import random
        idx = random.randint(0, len(self.image_history) - 1)
        item = self.image_history[idx]

        # 创建单列网格容器
        grid = GridLayout(
            cols=1,
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint_y=None
        )
        grid.bind(minimum_height=grid.setter('height'))

        # 计算图片区域可用高度
        image_area_height = Window.height - self.BOTTOM_HEIGHT - 10

        # 创建临时卡片
        temp_card = MDCard(
            orientation='vertical',
            size_hint_x=1,
            size_hint_y=None,
            height=image_area_height - 10,
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

        current_save = self.current_image
        self.image_container.clear_widgets()
        self.image_container.add_widget(grid)

        Clock.schedule_once(lambda dt: self._restore_current(current_save), 3)
        Snackbar(text=f"📋 历史: {item['prompt'][:20]}...").open()

    def _restore_current(self, current_save):
        self.image_container.clear_widgets()
        if current_save:
            self._update_display()
        else:
            self._update_display()

    def go_back(self):
        self.manager.current = 'main'