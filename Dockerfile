FROM python:3.9

# 安装Chrome和ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get install -y chromium-chromedriver

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY requirements.txt .
COPY scraper.py .

# 安装Python依赖
RUN pip install -r requirements.txt

# 设置环境变量
ENV GOOGLE_CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# 运行脚本
CMD ["python", "scraper.py"] 