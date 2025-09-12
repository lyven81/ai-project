# 🗓️ 黄道吉日 APP

**标准版MVP** - 专业的黄道吉日查询和择日推荐工具

## 📋 项目概述

黄道吉日APP是一款基于传统黄历文化的现代化Web应用，为用户提供准确、一致的择日建议。所有用户查询到的结果完全一致，不涉及个性化/八字/生肖等因素。

### 🎯 主要功能

- **每日宜忌**：显示当天公历/农历、节气、生肖、冲煞、宜/忌事项清单
- **日期查询**：支持任意日期查询黄历信息（公历⇄农历切换）
- **场景吉日推荐**：输入用途，系统推荐未来90天内的适合吉日
- **收藏与提醒**：收藏重要日期，设置提前提醒
- **多端适配**：移动端优先，支持Web和PWA

### 🌟 核心特点

- ✅ **标准化数据**：所有用户结果一致，基于传统黄历标准
- ✅ **专业算法**：基于五行、天干地支理论的择日算法
- ✅ **移动优先**：响应式设计，完美适配手机端
- ✅ **离线支持**：PWA技术，支持离线查询
- ✅ **简洁易用**：直观的界面设计，操作简单

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 1. 克隆项目

```bash
git clone <repository-url>
cd 黄道吉日APP
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 启动应用

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8080
```

### 5. 访问应用

- 前端界面：http://localhost:8080
- API文档：http://localhost:8080/docs
- API健康检查：http://localhost:8080/api/health

## 📱 用户使用场景

### 典型使用流程

1. **查看今日宜忌**：打开APP查看当天是否适合重要活动
2. **择日查询**：选择用途（结婚/搬家/开业等），获取推荐吉日
3. **收藏日期**：将重要日期加入收藏，设置提醒
4. **日期详情**：查询任意日期的详细黄历信息

### 支持的用途类型

- 🎊 **嫁娶（结婚）**：婚礼举办的最佳日期
- 🏠 **入宅（搬家）**：搬家、乔迁的适宜时机
- 🏢 **开市（开业）**：开业、签约的吉利日期
- 🗃️ **立券（签约）**：重要合同签署日期
- ✈️ **出行（旅行）**：旅游、出差的出发时机
- 🚧 **动土（施工）**：建筑、装修开工日期

## 🛠️ 技术架构

### 后端技术栈

- **框架**：FastAPI
- **数据库**：SQLite（可升级至PostgreSQL）
- **ORM**：SQLAlchemy
- **数据验证**：Pydantic
- **服务器**：Uvicorn

### 前端技术栈

- **基础**：HTML5 + CSS3 + JavaScript
- **样式**：CSS Grid + Flexbox
- **交互**：原生JavaScript（无框架依赖）
- **设计**：移动优先的响应式设计
- **PWA**：支持离线访问和桌面安装

### 数据模型

#### 黄历数据表 (days)
```sql
- id: 日期ID (YYYY-MM-DD)
- lunar_date: 农历日期
- zodiac_of_day: 当日生肖
- solar_term: 节气（可选）
- yi: 宜事项列表（JSON）
- ji: 忌事项列表（JSON）
- chong_zodiac: 冲煞生肖
- notes: 简明解释
```

#### 收藏表 (favorites)
```sql
- id: 收藏ID
- user_id: 用户ID
- date_id: 日期ID
- purpose: 用途类型
- remind_days_before: 提醒天数设置
- created_at: 创建时间
```

## 📡 API文档

### 核心API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/days/today` | 获取今日黄历信息 |
| GET | `/api/days/{date}` | 获取指定日期信息 |
| GET | `/api/recommend` | 获取吉日推荐 |
| POST | `/api/favorites` | 创建收藏 |
| GET | `/api/favorites` | 获取收藏列表 |
| DELETE | `/api/favorites/{id}` | 删除收藏 |
| POST | `/api/reminders/subscribe` | 设置提醒 |

### API使用示例

#### 获取今日黄历
```bash
curl -X GET "http://localhost:8080/api/days/today"
```

#### 查找结婚吉日
```bash
curl -X GET "http://localhost:8080/api/recommend?purpose=marriage&limit=5"
```

#### 创建收藏
```bash
curl -X POST "http://localhost:8080/api/favorites" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "date_id": "2025-10-01",
    "purpose": "marriage",
    "remind_days_before": [7, 3, 1]
  }'
```

## 🧪 测试

### 运行测试

```bash
# 运行API测试套件
python simple_test.py

# 如果有pytest环境
python -m pytest test_app.py -v
```

### 测试覆盖

- ✅ API端点测试（健康检查、日期查询、推荐、收藏）
- ✅ 数据模型测试
- ✅ 黄历算法测试
- ✅ 边界条件测试
- ✅ 错误处理测试

## 🐳 Docker部署

### 使用现有Dockerfile

```bash
# 构建镜像
docker build -t huangdao-app .

# 运行容器
docker run -d -p 8080:8080 huangdao-app
```

### Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/data
```

## ☁️ 云部署

### Google Cloud Run

```bash
# 构建并推送到GCR
gcloud builds submit --tag asia.gcr.io/PROJECT_ID/huangdao-app

# 部署到Cloud Run
gcloud run deploy huangdao-app \
  --image asia.gcr.io/PROJECT_ID/huangdao-app \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

### 其他云平台

- **AWS**：可部署至ECS、Lambda、或Elastic Beanstalk
- **Azure**：可部署至Container Instances或App Service
- **Heroku**：支持一键部署

## 📊 性能指标

### 响应时间

- 日期查询：< 200ms
- 吉日推荐：< 500ms
- 收藏操作：< 300ms

### 数据规模

- 预置90天黄历数据
- 支持无限用户收藏
- SQLite单文件，便于备份

### 资源消耗

- 内存：< 100MB
- 磁盘：< 50MB（含90天数据）
- CPU：低负载，适合小型VPS

## 🔧 配置选项

### 环境变量

```bash
PORT=8080                    # 服务端口
DATABASE_URL=sqlite:///./huangdao_calendar.db  # 数据库URL
```

### 数据扩展

```python
# 扩展到更多天数
python -c "
from init_db import *
from calendar_data import *
from datetime import date, timedelta

# 生成一年的数据
today = date.today()
data = generate_calendar_data(today, 365)
# ... 插入数据库
"
```

## 🛡️ 安全说明

- 无需收集用户敏感信息
- 本地化存储，保护隐私
- 无外部API依赖
- 静态种子数据，防止注入

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🆘 常见问题

### Q: 为什么某些日期没有推荐结果？
A: 这是正常现象。黄历根据传统算法，并非每日都适合所有活动。

### Q: 可以添加个性化功能吗？
A: 当前版本专注于标准化结果。个性化功能可在后续版本考虑。

### Q: 数据来源是否权威？
A: 基于传统黄历算法，简化实现。如需更高精度，建议咨询专业择日师。

### Q: 支持其他语言吗？
A: 当前版本为中文。国际化支持可在后续版本添加。

## 📞 联系方式

- 项目地址：[GitHub Repository]
- 问题反馈：[Issues Page]
- 邮箱：[Contact Email]

---

*🌟 感谢使用黄道吉日APP，祝您择日吉祥，万事如意！*