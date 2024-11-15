#!/bin/bash

# 安装 Python 和依赖
curl -o python.tar.gz https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
tar -xzf python.tar.gz
cd Python-3.9.7
./configure --enable-optimizations
make -j $(nproc)
make install

# 验证 Python 安装
python3 --version
which python3

# 安装 pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py

# 安装项目依赖
pip3 install -r requirements.txt

# 安装 Chrome 和 ChromeDriver
apt-get update
apt-get install -y wget gnupg2 unzip
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# 安装 ChromeDriver
CHROME_VERSION=$(google-chrome --version | cut -d " " -f3 | cut -d "." -f1)
wget -N https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}
CHROMEDRIVER_VERSION=$(cat LATEST_RELEASE_${CHROME_VERSION})
wget https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver