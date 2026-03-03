# ============================================
# 阶段 1: 前端构建
# ============================================
FROM node:20-alpine AS frontend-builder

# 设置工作目录
WORKDIR /frontend

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装前端依赖
RUN npm ci --only=production

# 复制前端源代码
COPY frontend/ ./

# 构建前端（输出到 dist/）
RUN npm run build

# ============================================
# 阶段 2: Python 依赖构建
# ============================================
FROM python:3.11-slim AS python-builder

# 设置工作目录
WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# 阶段 3: 最终运行镜像
# ============================================
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:$PATH" \
    PYTHONPATH="/install/lib/python3.11/site-packages:$PYTHONPATH"

# 安装运行时依赖（仅必需的）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 Python 依赖
COPY --from=python-builder /install /install

# 复制后端代码
COPY feishu_bot/ ./feishu_bot/
COPY lark_bot.py .
COPY wsgi.py .
COPY gunicorn.conf.py .

# 从前端构建阶段复制构建产物到 Flask 静态目录
COPY --from=frontend-builder /frontend/dist ./feishu_bot/web_admin/static

# 创建必要的目录
RUN mkdir -p /app/data /app/logs && \
    chmod 755 /app/data /app/logs

# 创建非 root 用户运行应用
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 暴露 Web 管理界面端口
EXPOSE 5000

# 设置健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 默认运行 Web 管理界面（使用 Gunicorn）
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
