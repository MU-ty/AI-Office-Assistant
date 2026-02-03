# 使用 Python 3.11 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# 使用国内镜像源加速 apt-get 安装 (针对 Debian Bookworm 优化)
RUN set -ex; \
    if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
        sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources; \
    fi; \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list || true; \
    sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list || true

# 安装系统依赖 (增加重试机制)
RUN apt-get update && \
    for i in {1..5}; do apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ffmpeg \
    libpq-dev && break || sleep 5; done \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip 并设置国内镜像源加速
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目配置文件
COPY pyproject.toml .

# 安装核心依赖 (去除了重型的本地 AI 库，如 torch/whisper)
# 这些功能将通过 API (如阿里云 DashScope) 提供
RUN pip install --no-cache-dir . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
