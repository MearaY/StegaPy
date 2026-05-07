FROM python:3.8-slim

# 指定工作目录
WORKDIR /app

# 配置环境变量：禁用字节码生成与标准输出缓冲
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 导入依赖清单
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝项目源码
COPY . .

# 暴露服务端口
EXPOSE 8501

# 设置容器启动入口
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
