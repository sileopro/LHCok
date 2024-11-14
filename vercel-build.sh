#!/bin/bash
# 安装 Chrome 和 ChromeDriver
apt-get update
apt-get install -y google-chrome-stable chromium-chromedriver

# 安装 Python 依赖
pip install -r requirements.txt 