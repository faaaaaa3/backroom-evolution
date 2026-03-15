# 后端运行指南

## 依赖安装

### 1. 安装 Python 依赖

确保已安装 Python 3.8+，然后安装所需的依赖包：

```bash
cd server
pip3 install -r requirements.txt
```

或者手动安装：

```bash
pip3 install fastapi==0.104.1
pip3 install uvicorn[standard]==0.24.0
pip3 install pydantic==2.5.0
pip3 install evermemos==0.3.6
pip3 install python-dotenv==1.0.0
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置必要的环境变量：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# EverMemOS API Configuration
EVERMEMOS_API_KEY=your_evermemos_api_key_here

# Default Group ID (optional)
DEFAULT_GROUP_ID=default_group

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

**重要**: 你需要从 EverMemOS 获取有效的 API Key 才能使用记忆存储功能。

## 运行后端服务器

### 方法 1: 直接运行

```bash
cd server
python3 main.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

### 方法 2: 使用启动脚本

Linux/Mac:
```bash
./start.sh
```

Windows:
```batch
start.bat
```

### 方法 3: 使用 uvicorn 直接运行

```bash
cd server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

`--reload` 选项会在代码变化时自动重启服务器（开发环境推荐）。

## API 端点

### 健康检查
```bash
curl http://localhost:8000/health
```

响应:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 存储记忆
```bash
curl -X POST http://localhost:8000/memories/store \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "memory": {
      "message_id": "msg_001",
      "create_time": "2024-01-01T00:00:00Z",
      "sender": "user123",
      "sender_name": "Test User",
      "content": "This is a test memory"
    }
  }'
```

### 批量查询记忆
```bash
curl -X POST http://localhost:8000/memories/batch-query \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {
        "user_id": "user123",
        "query": "test memory"
      }
    ]
  }'
```

## API 文档

启动服务器后，访问以下地址查看交互式 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 故障排除

### 端口被占用

如果端口 8000 被占用，可以指定其他端口：

```bash
python3 main.py --port 8001
```

或在 `main.py` 中修改默认端口：

```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # 修改这里的端口
```

### 依赖冲突

如果遇到依赖冲突，尝试创建虚拟环境：

```bash
cd server
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### EverMemOS API 错误

- **404 错误**: 检查 API Key 是否正确配置
- **认证失败**: 确认 EVERMEMOS_API_KEY 环境变量已设置
- **网络错误**: 检查网络连接和 EverMemOS 服务状态

## 开发建议

1. **使用虚拟环境**: 避免污染全局 Python 环境
2. **启用热重载**: 开发时使用 `--reload` 选项
3. **日志记录**: 查看控制台输出了解服务器运行状态
4. **API 测试**: 使用 Postman 集合 (`postman_collection.json`) 测试 API
5. **环境变量**: 敏感信息不要提交到版本控制

## 项目结构

```
server/
├── main.py                 # FastAPI 应用主文件
├── requirements.txt        # Python 依赖列表
├── .env                   # 环境变量配置（需自行创建）
├── .env.example           # 环境变量示例
├── start.sh               # Linux/Mac 启动脚本
├── start.bat              # Windows 启动脚本
├── test_client.py         # 测试客户端
├── advanced_client.py     # 高级客户端示例
└── postman_collection.json # Postman API 测试集合
```
