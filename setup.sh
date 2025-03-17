#!/bin/bash

echo "=== FastAPI Template 项目启动脚本 ==="

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 验证虚拟环境
if [ -z "$VIRTUAL_ENV" ]; then
    echo "虚拟环境激活失败，尝试使用绝对路径..."
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
    source "$SCRIPT_DIR/.venv/bin/activate"
    
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "虚拟环境激活失败，请手动激活后再运行此脚本"
        echo "运行: source .venv/bin/activate"
        exit 1
    fi
fi

echo "使用Python: $(which python)"
echo "使用pip: $(which pip)"

# 安装依赖
echo "安装项目依赖..."
pip install -r requirements.txt

# 从.env文件读取数据库和Redis配置
echo "读取配置..."
DB_USER=$(grep DB_USER .env | cut -d '=' -f2)
DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2)
DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2)

# 检查MySQL容器是否运行
echo "检查MySQL容器..."
MYSQL_CONTAINER=$(docker ps | grep mysql | awk '{print $1}')
if [ -z "$MYSQL_CONTAINER" ]; then
    echo "MySQL容器未运行，请先启动MySQL容器"
    echo "可以使用以下命令启动MySQL容器："
    echo "docker run --name mysql -e MYSQL_ROOT_PASSWORD=FastAPI@123 -p 3306:3306 -d mysql:8.0"
    exit 1
fi

# 检查Redis容器是否运行
echo "检查Redis容器..."
REDIS_CONTAINER=$(docker ps | grep redis | awk '{print $1}')
if [ -z "$REDIS_CONTAINER" ]; then
    echo "Redis容器未运行，请先启动Redis容器"
    echo "可以使用以下命令启动Redis容器："
    echo "docker run --name redis -p 6379:6379 -d redis:6.2"
    exit 1
fi

# 使用Docker命令创建数据库
echo "检查并创建数据库..."
echo "尝试在MySQL容器中创建数据库: $DB_NAME"

# 尝试在容器中创建数据库
docker exec $MYSQL_CONTAINER mysql -u$DB_USER -p$DB_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "数据库创建失败. 请检查MySQL容器的连接信息是否正确."
    echo "当前配置:"
    echo "用户: $DB_USER"
    echo "数据库: $DB_NAME"
    echo "容器ID: $MYSQL_CONTAINER"
    echo "尝试手动连接MySQL容器: docker exec -it $MYSQL_CONTAINER mysql -u$DB_USER -p"
    exit 1
fi

echo "数据库创建/检查成功!"

# 运行数据库迁移
echo "执行数据库迁移..."
python -m alembic revision --autogenerate -m "Initial migration" 2>/dev/null
python -m alembic upgrade head

# 启动服务
echo "启动 FastAPI 服务..."
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000