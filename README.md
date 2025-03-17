# FastAPI Template

基于 FastAPI 开发的现代化 Web 应用程序模板。

## 功能特点

已实现功能：
- 基于 FastAPI 的现代化 REST API
- MySQL 数据库支持
- Redis 缓存支持
  - 分布式缓存
  - 异步缓存支持
  - 自动序列化和反序列化
- 用户认证和授权系统
  - 用户注册
  - JWT 令牌认证
  - 基于角色的权限控制（RBAC）
  - 权限缓存
- CORS 跨域支持
- 结构化日志（使用 loguru）
- 环境变量配置
- API 文档自动生成
- 数据库迁移（使用 alembic）

## 技术栈

- 后端框架：FastAPI 0.115.8
- 数据库：MySQL 8.0
- 缓存：Redis 6.2
- Python 版本：3.10.11
- ORM：SQLAlchemy 2.0.27
- 数据验证：Pydantic 2.6.1
- 数据库迁移：Alembic 1.13.1
- 认证：JWT（python-jose 3.3.0）
- 密码加密：bcrypt 4.1.2
- 日志：loguru 0.7.2
- 权限框架：fastapi-permissions 0.2.7
- Redis客户端：redis 4.6.0, aioredis 2.0.1

## 项目结构

```
.
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   │   └── v1/           # API v1 版本
│   │       ├── api.py    # API 路由注册
│   │       └── endpoints/ # API 端点
│   │           └── auth.py # 认证相关接口
│   ├── core/             # 核心配置
│   │   └── config.py     # 配置管理
│   ├── db/               # 数据库相关
│   │   └── base.py       # 数据库配置
│   ├── models/           # 数据模型
│   │   ├── domain/      # 领域模型
│   │   │   └── user.py  # 用户模型
│   │   └── schemas/     # Pydantic 模型
│   │       ├── token.py # 令牌模型
│   │       └── user.py  # 用户数据模型
│   ├── services/         # 业务服务层
│   └── utils/           # 工具函数
│       └── security.py  # 安全工具函数
├── docs/                # 项目文档
├── migrations/         # 数据库迁移文件
├── .env              # 环境变量（从 .env.example 复制）
├── .env.example      # 环境变量示例
├── alembic.ini      # Alembic 配置
├── requirements.txt # 项目依赖
└── README.md       # 项目说明
```

## 快速开始

1. 克隆项目：
```bash
git clone <repository-url>
cd fastapi-template
```

2. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.\.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库和Redis配置
```

5. 设置Docker网络和容器：
```bash
# 运行Docker网络设置脚本
./docker-network.sh
```

6. 初始化并启动服务：
```bash
./setup.sh
```

## Docker环境配置

项目使用Docker容器运行MySQL和Redis服务，并通过Docker网络进行通信。

### Docker网络设置

项目使用名为`fastapi-network`的Docker网络，使容器之间可以通过容器名称相互访问。

```bash
# 创建网络
docker network create fastapi-network

# 将容器连接到网络
docker network connect fastapi-network mysql
docker network connect fastapi-network redis
```

### 容器配置

1. MySQL容器：
```bash
docker run --name mysql -e MYSQL_ROOT_PASSWORD=FastAPI@123 -p 3306:3306 -d mysql:8.0
```

2. Redis容器：
```bash
docker run --name redis -p 6379:6379 -d redis:6.2
```

3. 检查容器状态：
```bash
docker ps | grep mysql
docker ps | grep redis
```

### 环境变量配置

在`.env`文件中，数据库和Redis的主机名配置：

```ini
# 本地开发环境（macOS/Linux）
DB_HOST=localhost
DB_PORT=3306
REDIS_HOST=localhost
REDIS_PORT=6379

# Docker环境（容器间通信）
# DB_HOST=mysql
# DB_PORT=3306
# REDIS_HOST=redis
# REDIS_PORT=6379
```

**注意**：
- 在macOS和Linux上本地开发时，即使使用Docker容器，也应使用`localhost`作为主机名
- 在Docker Compose或Kubernetes环境中，可以使用容器名称作为主机名

## 缓存配置

Redis缓存配置（在 .env 文件中）：
```ini
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379/0
```

缓存特性：
- 支持同步和异步操作
- 自动序列化和反序列化（支持JSON和Pickle）
- 可配置的过期时间
- 分布式缓存支持
- 连接池管理
- 错误重试机制

使用缓存示例：
```python
from app.utils.cache import async_cache

@async_cache("user", 3600)  # 缓存1小时
async def get_user(user_id: int):
    return await db.query(User).filter(User.id == user_id).first()
```

## 接口文档

启动服务后，可以访问以下地址查看 API 文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 主要接口

#### 用户认证

- 用户注册
  ```http
  POST /api/v1/auth/register
  Content-Type: application/json
  
  {
    "email": "user@example.com",
    "username": "username",
    "password": "password",
    "full_name": "姓名"
  }
  ```

- 用户登录
  ```http
  POST /api/v1/auth/login
  Content-Type: application/x-www-form-urlencoded
  
  username=user@example.com&password=password
  ```

- 验证令牌
  ```http
  POST /api/v1/auth/test-token
  Authorization: Bearer <token>
  ```

## 配置说明

主要配置项（在 .env 文件中设置）：

```ini
# API配置
PROJECT_NAME=FastAPI-Template  # 项目名称
API_V1_STR=/api/v1          # API 版本路径
DEBUG=true                   # 调试模式
HOST=0.0.0.0                # 监听地址
PORT=8000                   # 监听端口

# 数据库配置
DB_HOST=localhost           # 数据库主机
DB_PORT=3306               # 数据库端口
DB_USER=your_username      # 数据库用户名
DB_PASSWORD=your_password  # 数据库密码
DB_NAME=auto_ai           # 数据库名称

# JWT配置
SECRET_KEY=your-key       # JWT 密钥
ALGORITHM=HS256          # JWT 算法
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 令牌过期时间（分钟）

# CORS配置
ALLOWED_ORIGINS=["*"]    # 允许的源
ALLOWED_METHODS=["*"]    # 允许的方法
ALLOWED_HEADERS=["*"]    # 允许的头部

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_URL=redis://localhost:6379/0
```

## 开发指南

### 代码规范

项目遵循以下代码规范：

1. **Python风格指南**：
   - 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)规范
   - 使用4个空格缩进
   - 行长度限制在100个字符以内
   - 使用snake_case命名变量和函数
   - 使用CamelCase命名类

2. **文档字符串**：
   - 使用Google风格的文档字符串
   - 为所有公共函数、方法和类添加文档字符串
   - 包含参数、返回值和异常的说明

3. **类型注解**：
   - 使用Python类型注解
   - 为所有函数参数和返回值添加类型注解
   - 使用Optional表示可能为None的值

4. **错误处理**：
   - 使用try-except捕获预期的异常
   - 记录异常信息到日志
   - 返回合适的错误响应

5. **日志记录**：
   - 使用loguru进行日志记录
   - 记录关键操作和错误信息
   - 使用适当的日志级别

### 最佳实践

1. **缓存使用**：
   - 使用Redis缓存频繁访问的数据
   - 设置合理的缓存过期时间
   - 在数据更新时清除相关缓存

2. **数据库操作**：
   - 使用SQLAlchemy ORM进行数据库操作
   - 在事务中执行数据库操作
   - 发生异常时回滚事务

3. **权限控制**：
   - 使用基于角色的访问控制（RBAC）
   - 为每个API端点添加权限检查
   - 缓存用户权限以提高性能

4. **API设计**：
   - 遵循RESTful API设计原则
   - 使用HTTP状态码表示操作结果
   - 返回统一的响应格式

5. **性能优化**：
   - 使用异步函数处理I/O操作
   - 缓存频繁访问的数据
   - 使用数据库索引优化查询

### 添加新功能

1. 创建数据模型：
   - 在 `app/models/domain/` 添加 SQLAlchemy 模型
   - 在 `app/models/schemas/` 添加 Pydantic 模型

2. 添加服务层代码：
   - 在 `app/services/` 添加服务层代码
   - 实现业务逻辑和数据库操作
   - 添加缓存支持

3. 添加新的 API 端点：
   - 在 `app/api/v1/endpoints/` 创建新的路由文件
   - 在 `app/api/v1/api.py` 注册路由
   - 添加权限控制

4. 更新数据库：
   ```bash
   alembic revision --autogenerate -m "添加新功能"
   alembic upgrade head
   ```

## 安全建议

1. 生产环境配置：
   - 使用强密码作为 `SECRET_KEY`
   - 禁用 `DEBUG` 模式
   - 限制 CORS 来源
   - 使用 HTTPS
   - 设置合适的令牌过期时间

2. 密码安全：
   - 使用 bcrypt 进行密码哈希
   - 密码最小长度：6位
   - 建议使用字母、数字和特殊字符组合

## 许可证

[MIT License](LICENSE)
