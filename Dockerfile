# 多阶段构建 - 前端构建阶段
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
# 设置Docker环境变量，使前端使用相对路径
ENV VITE_DOCKER=1
RUN npm run build

# 生产环境阶段
FROM python:3.12-alpine AS production

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apk add --no-cache \
    # nginx和ffmpeg
    nginx \
    ffmpeg \
    # pdf2image的核心依赖
    poppler-utils \
    && rm -rf /var/cache/apk/*

# Install dependencies using uv
RUN --mount=from=ghcr.io/astral-sh/uv:python3.12-alpine,source=/usr/local/bin/uv,target=/bin/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/.python-version,target=.python-version \
    uv sync --no-cache

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# 复制后端代码和资源文件
COPY backend/assets/ ./backend/assets/
COPY backend/app/ ./backend/app/

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV POPPLER_PATH=/usr/bin

# 暴露端口
EXPOSE 80
EXPOSE 8000

# 启动服务
CMD ["sh", "-c", "source .venv/bin/activate && cd backend && python -m app & nginx -g 'daemon off;'"]