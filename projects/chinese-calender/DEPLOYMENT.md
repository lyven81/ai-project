# 🚀 黄道吉日APP部署指南

本文档详细说明如何在不同环境中部署黄道吉日APP。

## 📋 部署前检查

### 系统要求

- **操作系统**：Linux、macOS或Windows
- **Python**：3.8或更高版本
- **内存**：至少512MB RAM
- **存储**：至少1GB可用空间
- **网络**：能够访问端口8080

### 依赖检查

```bash
# 检查Python版本
python --version

# 检查pip
pip --version

# （可选）检查Docker
docker --version
```

## 🏠 本地开发部署

### 方法一：使用启动脚本（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd 黄道吉日APP

# 2. 安装依赖
pip install -r requirements.txt

# 3. 使用启动脚本
python start.py

# 开发模式（自动重载）
python start.py --reload

# 指定端口
python start.py --port 3000

# 运行测试
python start.py --test
```

### 方法二：手动启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python init_db.py

# 3. 启动服务器
python -m uvicorn app:app --host 0.0.0.0 --port 8080

# 或使用reload模式
python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

### 访问应用

- **前端界面**：http://localhost:8080
- **API文档**：http://localhost:8080/docs
- **健康检查**：http://localhost:8080/api/health

## 🐳 Docker部署

### 单容器部署

```bash
# 构建镜像
docker build -t huangdao-app .

# 运行容器
docker run -d \
  --name huangdao-app \
  -p 8080:8080 \
  -v $(pwd)/data:/app/data \
  huangdao-app

# 查看日志
docker logs huangdao-app

# 停止容器
docker stop huangdao-app
```

### Docker Compose部署

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs app

# 停止服务
docker-compose down

# 生产环境启动（包含nginx）
docker-compose --profile production up -d
```

## ☁️ 云服务器部署

### VPS/云服务器通用步骤

1. **准备服务器**

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和pip
sudo apt install python3 python3-pip python3-venv -y

# 安装git
sudo apt install git -y

# （可选）安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. **部署应用**

```bash
# 克隆项目
git clone <repository-url>
cd 黄道吉日APP

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 使用nohup在后台运行
nohup python start.py --host 0.0.0.0 --port 8080 > app.log 2>&1 &
```

3. **设置系统服务**

创建systemd服务文件：

```bash
sudo nano /etc/systemd/system/huangdao-app.service
```

内容：

```ini
[Unit]
Description=HuangDao Calendar App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/黄道吉日APP
Environment=PATH=/home/ubuntu/黄道吉日APP/venv/bin
ExecStart=/home/ubuntu/黄道吉日APP/venv/bin/python start.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable huangdao-app
sudo systemctl start huangdao-app
sudo systemctl status huangdao-app
```

## 🌐 反向代理配置

### Nginx配置

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

### Apache配置

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8080/
    ProxyPassReverse / http://127.0.0.1:8080/
</VirtualHost>
```

## ☁️ 云平台部署

### Google Cloud Run

```bash
# 1. 构建并推送镜像
gcloud builds submit --tag gcr.io/PROJECT_ID/huangdao-app

# 2. 部署到Cloud Run
gcloud run deploy huangdao-app \
  --image gcr.io/PROJECT_ID/huangdao-app \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

### AWS ECS

1. 推送镜像到ECR
2. 创建任务定义
3. 创建服务
4. 配置负载均衡器

### Heroku

```bash
# 1. 登录Heroku
heroku login

# 2. 创建应用
heroku create huangdao-app

# 3. 部署
git push heroku main
```

### Railway

```bash
# 1. 安装Railway CLI
npm install -g @railway/cli

# 2. 登录并部署
railway login
railway init
railway up
```

## 🔧 环境配置

### 环境变量

创建`.env`文件：

```bash
# 服务器配置
PORT=8080
HOST=0.0.0.0

# 数据库配置
DATABASE_URL=sqlite:///./huangdao_calendar.db

# 日志配置
LOG_LEVEL=INFO

# 应用配置
APP_NAME=黄道吉日APP
APP_VERSION=1.0.0
```

### 生产环境配置

```bash
# 生产环境变量
export PYTHONPATH=/app
export PYTHONUNBUFFERED=1
export WORKERS=2
```

## 📊 监控和维护

### 健康检查

```bash
# 检查应用状态
curl http://localhost:8080/api/health

# 检查数据库
curl http://localhost:8080/api/stats
```

### 日志管理

```bash
# 查看应用日志
tail -f app.log

# 轮转日志
logrotate /etc/logrotate.d/huangdao-app
```

### 数据备份

```bash
# 备份数据库
cp huangdao_calendar.db backup/huangdao_calendar_$(date +%Y%m%d).db

# 自动化备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /app/huangdao_calendar.db /backup/huangdao_calendar_$DATE.db
find /backup -name "huangdao_calendar_*.db" -mtime +30 -delete
```

## 🔒 安全配置

### SSL/TLS配置

```bash
# 使用Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 防火墙配置

```bash
# UFW配置
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 安全头配置

在nginx配置中添加：

```nginx
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000";
```

## 🚨 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   sudo lsof -i :8080
   sudo kill -9 <PID>
   ```

2. **权限问题**
   ```bash
   sudo chown -R $USER:$USER .
   chmod +x start.py
   ```

3. **数据库问题**
   ```bash
   rm huangdao_calendar.db
   python init_db.py
   ```

4. **依赖问题**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### 性能优化

1. **使用Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn app:app -w 2 -b 0.0.0.0:8080
   ```

2. **启用缓存**
   ```python
   # 在app.py中添加
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.inmemory import InMemoryBackend
   
   FastAPICache.init(InMemoryBackend(), prefix="huangdao-cache")
   ```

3. **数据库优化**
   ```bash
   # 切换到PostgreSQL
   pip install psycopg2-binary
   export DATABASE_URL=postgresql://user:pass@localhost/dbname
   ```

## 📈 扩展部署

### 负载均衡

使用nginx upstream：

```nginx
upstream huangdao_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    location / {
        proxy_pass http://huangdao_backend;
    }
}
```

### 容器编排

Kubernetes部署文件：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: huangdao-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: huangdao-app
  template:
    metadata:
      labels:
        app: huangdao-app
    spec:
      containers:
      - name: huangdao-app
        image: huangdao-app:latest
        ports:
        - containerPort: 8080
```

---

## 📞 技术支持

如果在部署过程中遇到问题：

1. 检查[故障排除](#故障排除)章节
2. 查看应用日志
3. 提交Issue到项目仓库
4. 联系技术支持

**祝您部署顺利！** 🎉