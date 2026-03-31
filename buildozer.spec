[app]

# 应用信息
title = 建筑意向图
package.name = buildingapp
package.domain = org.buildingapp

# 源码配置
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv, __pycache__, .venv, .idea

# 版本
version = 1.0.0

# 依赖
requirements = python3==3.14.2,kivy==master

# 界面设置
orientation = portrait
fullscreen = 0

# Android 权限
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Android SDK/NDK 配置
android.api = 30
android.minapi = 21
android.ndk = 28c
android.gles = 2

# Python-for-android 配置
p4a.branch = develop
p4a.update = False
p4a.ignore_git = True

# Kivy 编译环境变量
env.KIVY_GL_BACKEND = sdl2
env.USE_OPENGL_ES2 = 1

# 自动接受许可证
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
