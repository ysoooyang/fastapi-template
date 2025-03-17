#!/bin/bash

echo "=== 设置Docker网络 ==="

# 创建Docker网络
echo "创建Docker网络: fastapi-network"
docker network create fastapi-network 2>/dev/null || echo "网络已存在"

# 检查MySQL容器
MYSQL_CONTAINER=$(docker ps -a | grep mysql | awk '{print $1}')
if [ -z "$MYSQL_CONTAINER" ]; then
    echo "MySQL容器不存在，创建新容器..."
    docker run --name mysql -e MYSQL_ROOT_PASSWORD=FastAPI@123 -p 3306:3306 -d mysql:8.0
    MYSQL_CONTAINER=$(docker ps | grep mysql | awk '{print $1}')
else
    # 检查容器是否运行
    MYSQL_RUNNING=$(docker ps | grep mysql | awk '{print $1}')
    if [ -z "$MYSQL_RUNNING" ]; then
        echo "启动MySQL容器..."
        docker start $MYSQL_CONTAINER
    else
        echo "MySQL容器已运行"
    fi
fi

# 检查Redis容器
REDIS_CONTAINER=$(docker ps -a | grep redis | awk '{print $1}')
if [ -z "$REDIS_CONTAINER" ]; then
    echo "Redis容器不存在，创建新容器..."
    docker run --name redis -p 6379:6379 -d redis:6.2
    REDIS_CONTAINER=$(docker ps | grep redis | awk '{print $1}')
else
    # 检查容器是否运行
    REDIS_RUNNING=$(docker ps | grep redis | awk '{print $1}')
    if [ -z "$REDIS_RUNNING" ]; then
        echo "启动Redis容器..."
        docker start $REDIS_CONTAINER
    else
        echo "Redis容器已运行"
    fi
fi

# 将容器连接到网络
echo "将MySQL容器连接到网络..."
docker network connect fastapi-network $MYSQL_CONTAINER 2>/dev/null || echo "MySQL容器已在网络中"

echo "将Redis容器连接到网络..."
docker network connect fastapi-network $REDIS_CONTAINER 2>/dev/null || echo "Redis容器已在网络中"

echo "网络设置完成！"
echo "MySQL容器ID: $MYSQL_CONTAINER"
echo "Redis容器ID: $REDIS_CONTAINER"
echo "现在你可以通过容器名称访问服务: mysql:3306 和 redis:6379" 