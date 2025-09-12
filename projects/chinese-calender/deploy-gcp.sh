#!/bin/bash

# 黄道吉日APP - Google Cloud部署脚本
# 使用方法: bash deploy-gcp.sh YOUR_PROJECT_ID

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查参数
if [ -z "$1" ]; then
    echo -e "${RED}❌ 错误: 请提供Google Cloud项目ID${NC}"
    echo "使用方法: bash deploy-gcp.sh YOUR_PROJECT_ID"
    exit 1
fi

PROJECT_ID="$1"
SERVICE_NAME="huangdao-app"
REGION="asia-east1"
IMAGE_URL="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo -e "${BLUE}🚀 黄道吉日APP - Google Cloud部署开始...${NC}"
echo "项目ID: $PROJECT_ID"
echo "服务名: $SERVICE_NAME"
echo "区域: $REGION"
echo "镜像: $IMAGE_URL"
echo ""

# 检查gcloud是否已安装
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Google Cloud CLI未安装，请先安装${NC}"
    echo "安装地址: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 检查是否已登录
echo -e "${YELLOW}🔐 检查Google Cloud登录状态...${NC}"
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  未登录Google Cloud，正在启动登录流程...${NC}"
    gcloud auth login
fi

# 设置默认项目
echo -e "${YELLOW}⚙️  设置默认项目...${NC}"
gcloud config set project $PROJECT_ID

# 检查项目是否存在
if ! gcloud projects describe $PROJECT_ID &> /dev/null; then
    echo -e "${RED}❌ 项目 $PROJECT_ID 不存在或无权限访问${NC}"
    exit 1
fi

# 启用必要的API服务
echo -e "${YELLOW}🔧 启用必要的API服务...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

echo -e "${GREEN}✅ API服务已启用${NC}"

# 检查Docker文件是否存在
if [ ! -f "Dockerfile" ]; then
    echo -e "${RED}❌ 未找到Dockerfile，请确保在项目根目录执行${NC}"
    exit 1
fi

# 构建Docker镜像
echo -e "${YELLOW}📦 构建Docker镜像...${NC}"
echo "这可能需要几分钟时间..."

if gcloud builds submit --tag $IMAGE_URL . ; then
    echo -e "${GREEN}✅ Docker镜像构建成功${NC}"
else
    echo -e "${RED}❌ Docker镜像构建失败${NC}"
    exit 1
fi

# 部署到Cloud Run
echo -e "${YELLOW}🌐 部署到Cloud Run...${NC}"

if gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_URL \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 80 \
  --max-instances 10 \
  --port 8080 \
  --set-env-vars PORT=8080 \
  --timeout 300; then
    echo -e "${GREEN}✅ 部署成功${NC}"
else
    echo -e "${RED}❌ 部署失败${NC}"
    exit 1
fi

# 获取服务URL
echo -e "${YELLOW}🔍 获取服务URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📱 访问您的黄道吉日APP:${NC}"
echo -e "${BLUE}🌍 URL: ${SERVICE_URL}${NC}"
echo -e "${BLUE}📖 API文档: ${SERVICE_URL}/docs${NC}"
echo -e "${BLUE}🔍 健康检查: ${SERVICE_URL}/api/health${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 测试部署
echo -e "${YELLOW}🧪 测试部署...${NC}"
if curl -s "${SERVICE_URL}/api/health" | grep -q "ok"; then
    echo -e "${GREEN}✅ 健康检查通过，应用运行正常${NC}"
else
    echo -e "${YELLOW}⚠️  健康检查失败，请检查应用日志${NC}"
    echo "查看日志: gcloud run logs read huangdao-app --region $REGION"
fi

# 显示有用的命令
echo ""
echo -e "${BLUE}📋 常用管理命令:${NC}"
echo "查看服务状态:"
echo "  gcloud run services describe $SERVICE_NAME --region $REGION"
echo ""
echo "查看实时日志:"
echo "  gcloud run logs tail $SERVICE_NAME --region $REGION"
echo ""
echo "更新服务:"
echo "  bash deploy-gcp.sh $PROJECT_ID"
echo ""
echo "删除服务:"
echo "  gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""

# 显示成本信息
echo -e "${BLUE}💰 成本信息:${NC}"
echo "Cloud Run提供慷慨的免费额度："
echo "• 每月200万次请求"
echo "• 400,000 GB·秒的计算时间"
echo "• 200,000 vCPU·秒的CPU时间"
echo "对于大多数小型应用，完全免费！"
echo ""

echo -e "${GREEN}🎯 部署脚本执行完成！祝您使用愉快！${NC}"