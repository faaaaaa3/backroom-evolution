from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import os
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="EverMemOS Memory Server",
    description="A FastAPI server for storing and querying memories using EverMemOS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Webpack dev server
        "http://127.0.0.1:8080",
        "http://localhost:3000",  # Alternative common port
        "http://127.0.0.1:3000",
        "*",  # Allow all origins for development (can be restricted in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configuration
EVERMEMOS_API_KEY = os.getenv("EVERMEMOS_API_KEY", "")
DEFAULT_GROUP_ID = os.getenv("DEFAULT_GROUP_ID", "default_group")
USE_MOCK_MODE = os.getenv("USE_MOCK_MODE", "false").lower() == "true"
EVERMEMOS_BASE_URL = os.getenv("EVERMEMOS_BASE_URL", "https://api.evermind.ai/api/v1")

# Initialize HTTP client for API calls
http_client = httpx.AsyncClient(timeout=30.0)

# Print configuration status
if USE_MOCK_MODE:
    print("⚠️  Running in MOCK MODE - memories will not be persisted")
else:
    if not EVERMEMOS_API_KEY or EVERMEMOS_API_KEY == "your_evermemos_api_key_here":
        print("⚠️  EVERMEMOS_API_KEY is not configured! Please set it in .env file")
        print("📝 You can get an API key from: https://console.evermind.ai")
        print("🔄 Falling back to MOCK MODE\n")
        #USE_MOCK_MODE = True
    else:
        print(f"✅ EverMemOS API configured: {EVERMEMOS_BASE_URL}")
        print(f"🔑 API Key: {'*' * len (EVERMEMOS_API_KEY)}\n")

# Initialize EverMemOS
if USE_MOCK_MODE:
    print("⚠️  Running in MOCK MODE - memories will not be persisted")
    memory_service = None
else:
    try:
        memory_service = EverMemOS(api_key=EVERMEMOS_API_KEY).v1.memories
        print("✅ EverMemOS initialized successfully")
    except Exception as e:
        print(f"⚠️  Failed to initialize EverMemOS: {e}")
        print("📝 Falling back to MOCK MODE")


class MemoryInput(BaseModel):
    """Memory input model for storing a single memory"""
    message_id: str = Field(..., description="Unique identifier for the message")
    create_time: str = Field(..., description="ISO 8601 formatted timestamp")
    sender: str = Field(..., description="User ID of the sender")
    sender_name: str = Field(..., description="Display name of the sender")
    content: str = Field(..., description="The memory content to store")
    group_id: Optional[str] = Field(None, description="Optional group ID, defaults to DEFAULT_GROUP_ID")


class StoreMemoryRequest(BaseModel):
    """Request model for storing memory"""
    user_id: str = Field(..., description="User ID to associate with this memory")
    memory: MemoryInput


class StoreMemoryResponse(BaseModel):
    """Response model for storing memory"""
    status: str
    message: str
    request_id: str


class BatchStoreRequest(BaseModel):
    """Request model for batch storing memories"""
    messages: List[MemoryInput] = Field(..., description="List of memories to store")


class BatchStoreResult(BaseModel):
    """Result for a single memory in batch store operation"""
    message_id: str
    success: bool
    error: Optional[str] = None


class BatchStoreResponse(BaseModel):
    """Response model for batch storing memories"""
    status: str
    message: str
    results: List[BatchStoreResult]
    total_count: int
    success_count: int
    failed_count: int


class QueryPair(BaseModel):
    """Query pair for batch memory search"""
    user_id: str = Field(..., description="User ID to search memories for")
    query: str = Field(..., description="Search query string")


class BatchQueryRequest(BaseModel):
    """Request model for batch querying memories"""
    queries: List[QueryPair] = Field(..., description="List of (user_id, query) pairs to search")


class QueryResult(BaseModel):
    """Result for a single query in batch search"""
    user_id: str
    query: str
    total_count: int
    success: bool
    error: Optional[str] = None


class BatchQueryResponse(BaseModel):
    """Response model for batch querying memories"""
    results: List[QueryResult]




@app.post("/memories/batch-store", response_model=BatchStoreResponse, summary="Batch store memories")
async def batch_store_memories(request: BatchStoreRequest):
    """
    Batch store multiple memories.
    
    - **messages**: List of memory objects to store, each containing:
        - **message_id**: Unique identifier for the message
        - **create_time**: ISO 8601 formatted timestamp
        - **sender**: User ID of the sender
        - **sender_name**: Display name of the sender
        - **content**: The memory content
        - **group_id**: Optional group ID
    
    Returns results for each memory with success/failure status.
    Partial failures will not rollback successful stores.
    """
    if USE_MOCK_MODE:
        # Mock mode - simulate successful storage
        print(f"📝 [MOCK] Batch storing {len(request.messages)} memories...")
        results = []
        for msg in request.messages:
            results.append(BatchStoreResult(
                message_id=msg.message_id,
                success=True,
                error=None
            ))
        
        return BatchStoreResponse(
            status="success",
            message=f"Successfully stored {len(request.messages)} memories (mock mode)",
            results=results,
            total_count=len(request.messages),
            success_count=len(request.messages),
            failed_count=0
        )
    
    results = []
    success_count = 0
    failed_count = 0

    headers = {
        "Authorization": f"Bearer {EVERMEMOS_API_KEY}",
        "Content-Type": "application/json"
    }
    import time
    for memory_input in request.messages:
        try:
            # Prepare memory data
            memory_data = {
                "user_id": memory_input.sender,
                "async_mode":False,
                "messages":[{
                    
                    # some extra info, can be removed
                    "message_id": memory_input.message_id,
                    "create_time": memory_input.create_time,
                    "sender": memory_input.sender,
                    "sender_name": memory_input.sender_name,
                    
                    # the follower is what the server uses.
                    "content": memory_input.content,
                    "role":"user",
                    "timestamp": int(time.time())
                }]
            }
            
            # Add optional fields if provided
            #if memory_input.group_id:
            #    memory_data["group_id"] = memory_input.group_id
            #else:
            #    memory_data["group_id"] = DEFAULT_GROUP_ID
            
            # Call EverMemOS API directly
            print(f"📡 Storing memory {memory_input.message_id}...{memory_input.sender}->memory_input.content")
            
            response = await http_client.post(
                f"{EVERMEMOS_BASE_URL}/memories",
                headers=headers,
                json=memory_data
            )
            
            print(f"📥 Response for {memory_input.message_id}: {response.status_code}")
            
            if response.status_code == 200:
                print("store response", response.json())
                results.append(BatchStoreResult(
                    message_id=memory_input.message_id,
                    success=True,
                    error=None
                ))
                success_count += 1
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Failed to store {memory_input.message_id}: {error_msg}")
                results.append(BatchStoreResult(
                    message_id=memory_input.message_id,
                    success=False,
                    error=error_msg
                ))
                failed_count += 1
                
        except httpx.HTTPError as e:
            print(e)
            error_msg = str(e)
            print(f"❌ HTTP error storing {memory_input.message_id}: {error_msg}")
            results.append(BatchStoreResult(
                message_id=memory_input.message_id,
                success=False,
                error=error_msg
            ))
            failed_count += 1
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error storing {memory_input.message_id}: {error_msg}")
            results.append(BatchStoreResult(
                memory_input.message_id,
                success=False,
                error=error_msg
            ))
            failed_count += 1
    print(results)
    return BatchStoreResponse(
        status="partial_success" if failed_count > 0 else "success",
        message=f"Stored {success_count} of {len(request.messages)} memories successfully",
        results=results,
        total_count=len(request.messages),
        success_count=success_count,
        failed_count=failed_count
    )


@app.post("/memories/batch-query", response_model=BatchQueryResponse, summary="Batch query memories")
async def batch_query_memories(request: BatchQueryRequest):
    """
    Batch query memories for multiple (user_id, query) pairs.
    
    - **queries**: List of query pairs, each containing:
        - **user_id**: User ID to search memories for
        - **query**: Search query string
    
    Returns results for each query with total count of matching memories.
    """
    if USE_MOCK_MODE:
        # Mock mode - return empty results
        print(f"📝 [MOCK] Batch querying {len(request.queries)} queries...")
        results = []
        for query_pair in request.queries:
            results.append(QueryResult(
                user_id=query_pair.user_id,
                query=query_pair.query,
                total_count=0,
                success=True,
                error=None
            ))
        return BatchQueryResponse(results=results)
    
    results = []
    
    headers = {
        "Authorization": f"Bearer {EVERMEMOS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for query_pair in request.queries:
        try:
            # Prepare search data for EverMemOS API
            # Following the curl example: 
            # curl -X POST "https://api.evermind.ai/api/v0/memories/search" \
            #   -H "Authorization: Bearer <YOUR_API_KEY>" \
            #   -H "Content-Type: application/json" \
            #   -d '{ "user_id": "user_demo_001", "query": "coffee preference" }'
            search_data = {
                "filters":{"user_id": query_pair.user_id},
                "query": query_pair.query,
                "method":"hybrid",
                "memory_types":["episodic_memory", "profile", "raw_message", "agent_memory"],
                "top_k":5
            }
            
            print(f"📡 Querying memories for {query_pair.user_id}: {query_pair.query}")
            print(f"📦 Request data: {search_data}")
            
            # Call EverMemOS search API using POST method (as per curl example with -d flag)
            response = await http_client.post(
                f"{EVERMEMOS_BASE_URL}/memories/search",
                headers=headers,
                json=search_data
            )
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response body: {response.text[:200]}")
            
            if response.status_code == 200:
                api_response = response.json()
                print("memeory response", api_response)
                # Extract memories array from response
                # Expected format: {"memories": [...], "total_count": N} or similar
                if isinstance(api_response, dict) and "data" in api_response and isinstance(api_response["data"], dict):
                    memories = api_response["data"].get("raw_messages", [])
                    total_count = api_response["data"].get("total_count", len(memories))
                else:
                    memories = []
                    total_count = 0
                import json
                results.append(QueryResult(
                    user_id=query_pair.user_id,
                    query=query_pair.query + "->(" + json.dumps(memories) + ")",
                    total_count=total_count,
                    success=True,
                    error=None
                ))
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"❌ Query failed for {query_pair.user_id}: {error_msg}")
                results.append(QueryResult(
                    user_id=query_pair.user_id,
                    query=query_pair.query,
                    total_count=0,
                    success=False,
                    error=error_msg
                ))
                
        except httpx.HTTPError as e:
            error_msg = str(e)
            print(f"❌ HTTP error querying {query_pair.user_id}: {error_msg}")
            results.append(QueryResult(
                user_id=query_pair.user_id,
                query=query_pair.query,
                total_count=0,
                success=False,
                error=error_msg
            ))
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error querying {query_pair.user_id}: {error_msg}")
            results.append(QueryResult(
                user_id=query_pair.user_id,
                query=query_pair.query,
                total_count=0,
                success=False,
                error=error_msg
            ))
    print(results)
    return BatchQueryResponse(results=results)


@app.get("/health", summary="Health check endpoint")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
