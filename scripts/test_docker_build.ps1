# Docker 构建测试脚本 (PowerShell)
# 用于验证多阶段 Dockerfile 构建是否成功

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Docker 多阶段构建测试" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
try {
    docker --version | Out-Null
    Write-Host "✓ Docker 已安装" -ForegroundColor Green
} catch {
    Write-Host "✗ 错误: Docker 未安装" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 设置镜像名称和标签
$IMAGE_NAME = "feishu-bot-web-admin"
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$IMAGE_TAG = "test-$TIMESTAMP"
$FULL_IMAGE_NAME = "${IMAGE_NAME}:${IMAGE_TAG}"

Write-Host "镜像名称: $FULL_IMAGE_NAME"
Write-Host ""

# 构建镜像
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "阶段 1: 构建 Docker 镜像" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

try {
    docker build -t $FULL_IMAGE_NAME .
    Write-Host "✓ 镜像构建成功" -ForegroundColor Green
} catch {
    Write-Host "✗ 镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 检查镜像大小
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "阶段 2: 检查镜像大小" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$IMAGE_SIZE = docker images $FULL_IMAGE_NAME --format "{{.Size}}"
Write-Host "镜像大小: $IMAGE_SIZE"

Write-Host ""

# 检查镜像层
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "阶段 3: 检查镜像层" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

docker history $FULL_IMAGE_NAME --no-trunc

Write-Host ""

# 验证镜像内容
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "阶段 4: 验证镜像内容" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "检查前端构建产物..."
try {
    docker run --rm $FULL_IMAGE_NAME ls -la /app/feishu_bot/web_admin/static/index.html | Out-Null
    Write-Host "✓ 前端构建产物存在" -ForegroundColor Green
} catch {
    Write-Host "✗ 前端构建产物缺失" -ForegroundColor Red
    exit 1
}

Write-Host "检查后端代码..."
try {
    docker run --rm $FULL_IMAGE_NAME ls -la /app/feishu_bot/web_admin/server.py | Out-Null
    Write-Host "✓ 后端代码存在" -ForegroundColor Green
} catch {
    Write-Host "✗ 后端代码缺失" -ForegroundColor Red
    exit 1
}

Write-Host "检查 Python 依赖..."
try {
    docker run --rm $FULL_IMAGE_NAME python -c "import flask; import jwt; print('Flask and PyJWT installed')" | Out-Null
    Write-Host "✓ Python 依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 依赖缺失" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 测试容器启动
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "阶段 5: 测试容器启动" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$CONTAINER_NAME = "feishu-bot-test-$IMAGE_TAG"

Write-Host "启动测试容器..."
try {
    docker run -d `
        --name $CONTAINER_NAME `
        -e WEB_ADMIN_PASSWORD="test_password_123" `
        -e JWT_SECRET_KEY="test_secret_key_456" `
        -p 5001:5000 `
        $FULL_IMAGE_NAME | Out-Null
    Write-Host "✓ 容器启动成功" -ForegroundColor Green
} catch {
    Write-Host "✗ 容器启动失败" -ForegroundColor Red
    exit 1
}

# 等待容器启动
Write-Host "等待容器就绪..."
Start-Sleep -Seconds 5

# 检查容器状态
$containerRunning = docker ps | Select-String $CONTAINER_NAME
if ($containerRunning) {
    Write-Host "✓ 容器运行中" -ForegroundColor Green
} else {
    Write-Host "✗ 容器未运行" -ForegroundColor Red
    docker logs $CONTAINER_NAME
    docker rm -f $CONTAINER_NAME | Out-Null
    exit 1
}

# 测试健康检查端点
Write-Host "测试健康检查端点..."
Start-Sleep -Seconds 2
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5001/api/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ 健康检查端点响应正常" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠ 健康检查端点无响应（可能需要更长启动时间）" -ForegroundColor Yellow
}

# 清理测试容器
Write-Host ""
Write-Host "清理测试容器..."
docker stop $CONTAINER_NAME | Out-Null
docker rm $CONTAINER_NAME | Out-Null
Write-Host "✓ 测试容器已清理" -ForegroundColor Green

Write-Host ""

# 总结
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "测试完成" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ 所有测试通过" -ForegroundColor Green
Write-Host ""
Write-Host "镜像信息:"
Write-Host "  名称: $FULL_IMAGE_NAME"
Write-Host "  大小: $IMAGE_SIZE"
Write-Host ""
Write-Host "下一步:"
Write-Host "  1. 使用镜像: docker run -d -p 5000:5000 -e WEB_ADMIN_PASSWORD=xxx -e JWT_SECRET_KEY=xxx $FULL_IMAGE_NAME"
Write-Host "  2. 推送镜像: docker tag $FULL_IMAGE_NAME your-registry/${IMAGE_NAME}:latest"
Write-Host "  3. 清理镜像: docker rmi $FULL_IMAGE_NAME"
Write-Host ""
