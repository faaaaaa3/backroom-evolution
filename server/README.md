# EverMemOS Memory Server

A FastAPI server for storing and querying memories using EverMemOS.

## Features

- **Store Memory**: Store a memory for a specific user
- **Batch Query**: Query memories for multiple (user_id, query) pairs in a single request
- **Health Check**: Simple endpoint to verify server status

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your configuration:

```bash
cp .env.example .env
```

Edit `.env` file:
```
EVERMEMOS_API_KEY=your_actual_api_key
DEFAULT_GROUP_ID=your_default_group_id
```

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### 1. Store Memory

**POST** `/memories/store`

Store a memory for a specific user.

**Request Body:**
```json
{
  "user_id": "user_demo_001",
  "memory": {
    "message_id": "msg_001",
    "create_time": "2025-01-15T10:00:00Z",
    "sender": "user_demo_001",
    "sender_name": "Demo User",
    "content": "I like black Americano, no sugar, the stronger the better!",
    "group_id": "group_001"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Memory stored successfully",
  "request_id": "req_123456"
}
```

### 2. Batch Query Memories

**POST** `/memories/batch-query`

Query memories for multiple (user_id, query) pairs.

**Request Body:**
```json
{
  "queries": [
    {
      "user_id": "user_demo_001",
      "query": "coffee preference"
    },
    {
      "user_id": "user_demo_002",
      "query": "food preferences"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "user_id": "user_demo_001",
      "query": "coffee preference",
      "total_count": 3,
      "success": true,
      "error": null
    },
    {
      "user_id": "user_demo_002",
      "query": "food preferences",
      "total_count": 5,
      "success": true,
      "error": null
    }
  ]
}
```

### 3. Health Check

**GET** `/health`

Check server health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example Usage

### Using curl

**Store a memory:**
```bash
curl -X POST "http://localhost:8000/memories/store" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo_001",
    "memory": {
      "message_id": "msg_001",
      "create_time": "2025-01-15T10:00:00Z",
      "sender": "user_demo_001",
      "sender_name": "Demo User",
      "content": "I like black Americano, no sugar, the stronger the better!",
      "group_id": "group_001"
    }
  }'
```

**Batch query memories:**
```bash
curl -X POST "http://localhost:8000/memories/batch-query" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"user_id": "user_demo_001", "query": "coffee preference"},
      {"user_id": "user_demo_002", "query": "food preferences"}
    ]
  }'
```

### Using Python

```python
import requests

# Store memory
store_response = requests.post(
    "http://localhost:8000/memories/store",
    json={
        "user_id": "user_demo_001",
        "memory": {
            "message_id": "msg_001",
            "create_time": "2025-01-15T10:00:00Z",
            "sender": "user_demo_001",
            "sender_name": "Demo User",
            "content": "I like black Americano!",
            "group_id": "group_001"
        }
    }
)
print(store_response.json())

# Batch query
query_response = requests.post(
    "http://localhost:8000/memories/batch-query",
    json={
        "queries": [
            {"user_id": "user_demo_001", "query": "coffee preference"}
        ]
    }
)
print(query_response.json())
```

## Error Handling

The server handles errors gracefully:
- Invalid request data returns 422 Validation Error
- EverMemOS API errors return 500 Internal Server Error
- Each query in batch operations is handled independently

## Notes

- All timestamps should be in ISO 8601 format (e.g., "2025-01-15T10:00:00Z")
- The `sender` field in stored memories is automatically set to the `user_id` from the request
- If `group_id` is not provided, the default group ID from environment variables is used
- Batch queries continue processing even if individual queries fail
