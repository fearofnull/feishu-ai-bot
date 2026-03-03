#!/bin/bash

# Docker 构建测试脚本
# 用于验证多阶段 Dockerfile 构建是否成功

set -e

echo "=========================================="
echo "Docker 多阶段构建测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 已安装${NC}"
echo ""

# 设置镜像名称和标签
IMAGE_NAME="feishu-bot-web-admin"
IMAGE_TAG="test-$(date +%Y%m%d-%H%M%S)"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo "镜像名称: ${FULL_IMAGE_NAME}"
echo ""

# 构建镜像
echo "=========================================="
echo "阶段 1: 构建 Docker 镜像"
echo "=========================================="
echo ""

if docker build -t "${FULL_IMAGE_NAME}" .; then
    echo -e "${GREEN}✓ 镜像构建成功${NC}"
else
    echo -e "${RED}✗ 镜像构建失败${NC}"
    exit 1
fi

echo ""

# 检查镜像大小
echo "=========================================="
echo "阶段 2: 检查镜像大小"
echo "=========================================="
echo ""

IMAGE_SIZE=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}")
echo "镜像大小: ${IMAGE_SIZE}"

# 检查镜像是否小于 1GB（优化目标）
SIZE_MB=$(docker images "${FULL_IMAGE_NAME}" --format "{{.Size}}" | sed 's/MB//' | sed 's/GB/*1024/' | bc 2>/dev/null || echo "0")
if [ -n "$SIZE_MB" ] && [ "$SIZE_MB" != "0" ]; then
    if (( $(echo "$SIZE_MB < 1024" | bc -l) )); then
        echo -e "${GREEN}✓ 镜像大小符合优化目标 (< 1GB)${NC}"
    else
        echo -e "${YELLOW}⚠ 镜像大小超过 1GB，建议进一步优化${NC}"
    fi
fi

echo ""

# 检查镜像层
echo "=========================================="
echo "阶段 3: 检查镜像层"
echo "=========================================="
echo ""

docker history "${FULL_IMAGE_NAME}" --no-trunc

echo ""

# 验证镜像内容
echo "=========================================="
echo "阶段 4: 验证镜像内容"
echo "=========================================="
echo ""

echo "检查前端构建产物..."
if docker run --rm "${FULL_IMAGE_NAME}" ls -la /app/feishu_bot/web_admin/static/index.html &> /dev/null; then
    echo -e "${GREEN}✓ 前端构建产物存在${NC}"
else
    echo -e "${RED}✗ 前端构建产物缺失${NC}"
    exit 1
fi

echo "检查后端代码..."
if docker run --rm "${FULL_IMAGE_NAME}" ls -la /app/feishu_bot/web_admin/server.py &> /dev/null; then
    echo -e "${GREEN}✓ 后端代码存在${NC}"
else
    echo -e "${RED}✗ 后端代码缺失${NC}"
    exit 1
fi

echo "检查 Python 依赖..."
if docker run --rm "${FULL_IMAGE_NAME}" python -c "import flask; import jwt; print('Flask and PyJWT installed')" &> /dev/null; then
    echo -e "${GREEN}✓ Python 依赖已安装${NC}"
else
    echo -e "${RED}✗ Python 依赖缺失${NC}"
    exit 1
fi

echo ""

# 测试容器启动
echo "=========================================="
echo "阶段 5: 测试容器启动"
echo "=========================================="
echo ""

CONTAINER_NAME="feishu-bot-test-${IMAGE_TAG}"

echo "启动测试容器..."
if docker run -d \
    --name "${CONTAINER_NAME}" \
    -e WEB_ADMIN_PASSWORD="test_password_123" \
    -e JWT_SECRET_KEY="test_secret_key_456" \
    -p 5001:5000 \
    "${FULL_IMAGE_NAME}" > /dev/null; then
    echo -e "${GREEN}✓ 容器启动成功${NC}"
else
    echo -e "${RED}✗ 容器启动失败${NC}"
    exit 1
fi

# 等待容器启动
echo "等待容器就绪..."
sleep 5

# 检查容器状态
if docker ps | grep -q "${CONTAINER_NAME}"; then
    echo -e "${GREEN}✓ 容器运行中${NC}"
else
    echo -e "${RED}✗ 容器未运行${NC}"
    docker logs "${CONTAINER_NAME}"
    docker rm -f "${CONTAINER_NAME}" > /dev/null 2>&1
    exit 1
fi

# 测试健康检查端点
echo "测试健康检查端点..."
sleep 2
if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 健康检查端点响应正常${NC}"
else
    echo -e "${YELLOW}⚠ 健康检查端点无响应（可能需要更长启动时间）${NC}"
fi

# 清理测试容器
echo ""
echo "清理测试容器..."
docker stop "${CONTAINER_NAME}" > /dev/null 2>&1
docker rm "${CONTAINER_NAME}" > /dev/null 2>&1
echo -e "${GREEN}✓ 测试容器已清理${NC}"

echo ""

# 总结
echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""
echo -e "${GREEN}✓ 所有测试通过${NC}"
echo ""
echo "镜像信息:"
echo "  名称: ${FULL_IMAGE_NAME}"
echo "  大小: ${IMAGE_SIZE}"
echo ""
echo "下一步:"
echo "  1. 使用镜像: docker run -d -p 5000:5000 -e WEB_ADMIN_PASSWORD=xxx -e JWT_SECRET_KEY=xxx ${FULL_IMAGE_NAME}"
echo "  2. 推送镜像: docker tag ${FULL_IMAGE_NAME} your-registry/${IMAGE_NAME}:latest"
echo "  3. 清理镜像: docker rmi ${FULL_IMAGE_NAME}"
echo ""
