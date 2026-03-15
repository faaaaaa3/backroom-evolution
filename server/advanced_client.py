#!/usr/bin/env python3
"""
Advanced example demonstrating batch operations and error handling
"""

import requests
from datetime import datetime
import json
from typing import List, Dict

BASE_URL = "http://localhost:8000"


class MemoryClient:
    """Client for interacting with EverMemOS Memory Server"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def store_memory(self, user_id: str, content: str, 
                     sender_name: str = "User", 
                     group_id: str = None) -> Dict:
        """Store a single memory for a user"""
        
        payload = {
            "user_id": user_id,
            "memory": {
                "message_id": f"msg_{datetime.now().timestamp()}_{user_id}",
                "create_time": datetime.utcnow().isoformat() + "Z",
                "sender": user_id,
                "sender_name": sender_name,
                "content": content,
                "group_id": group_id
            }
        }
        
        response = self.session.post(
            f"{self.base_url}/memories/store",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def store_multiple_memories(self, user_id: str, 
                                contents: List[str]) -> List[Dict]:
        """Store multiple memories for a user"""
        results = []
        for content in contents:
            try:
                result = self.store_memory(user_id, content)
                results.append({"success": True, "result": result})
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        return results
    
    def batch_query(self, queries: List[Dict[str, str]]) -> Dict:
        """
        Batch query memories for multiple (user_id, query) pairs
        
        Args:
            queries: List of dicts with 'user_id' and 'query' keys
        
        Returns:
            Dict containing results for each query
        """
        payload = {"queries": queries}
        
        response = self.session.post(
            f"{self.base_url}/memories/batch-query",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def query_user_memories(self, user_id: str, 
                           queries: List[str]) -> Dict:
        """
        Query multiple questions for a single user
        
        Args:
            user_id: The user ID to search memories for
            queries: List of query strings
        
        Returns:
            Dict containing results for each query
        """
        query_pairs = [{"user_id": user_id, "query": q} for q in queries]
        return self.batch_query(query_pairs)


def example_usage():
    """Demonstrate various usage patterns"""
    
    client = MemoryClient()
    
    # Example 1: Store multiple memories for a user
    print("Example 1: Storing multiple memories")
    print("-" * 60)
    
    user_memories = {
        "user_001": [
            "I prefer coffee without sugar",
            "My favorite drink is black Americano",
            "I drink coffee every morning at 8 AM",
            "I don't like tea or energy drinks"
        ],
        "user_002": [
            "I love pizza and pasta",
            "My favorite cuisine is Italian",
            "I'm allergic to peanuts",
            "I prefer home-cooked meals"
        ]
    }
    
    for user_id, memories in user_memories.items():
        print(f"\nStoring {len(memories)} memories for {user_id}")
        results = client.store_multiple_memories(user_id, memories)
        successful = sum(1 for r in results if r['success'])
        print(f"✅ Successfully stored {successful}/{len(memories)} memories")
    
    # Example 2: Batch query for different users
    print("\n\nExample 2: Batch querying multiple users")
    print("-" * 60)
    
    queries = [
        {"user_id": "user_001", "query": "coffee preferences"},
        {"user_id": "user_001", "query": "drink habits"},
        {"user_id": "user_002", "query": "food preferences"},
        {"user_id": "user_002", "query": "dietary restrictions"}
    ]
    
    results = client.batch_query(queries)
    
    print("\nQuery Results:")
    for result in results['results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['user_id']}: '{result['query']}' -> {result['total_count']} memories")
    
    # Example 3: Query multiple questions for one user
    print("\n\nExample 3: Multiple queries for single user")
    print("-" * 60)
    
    user_queries = [
        "beverage preferences",
        "morning routine",
        "dislikes"
    ]
    
    results = client.query_user_memories("user_001", user_queries)
    
    print(f"\nQuerying user_001 for {len(user_queries)} topics:")
    for result in results['results']:
        print(f"  - '{result['query']}': {result['total_count']} matches")


def error_handling_example():
    """Demonstrate error handling"""
    print("\n\nExample 4: Error Handling")
    print("-" * 60)
    
    client = MemoryClient()
    
    # Try to store memory with invalid data
    try:
        client.store_memory("", "Invalid user ID")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error caught: {e.response.status_code}")
    
    # Try batch query with empty queries
    try:
        client.batch_query([])
    except requests.exceptions.HTTPError as e:
        print(f"Empty query list error: {e.response.status_code}")


if __name__ == "__main__":
    print("🚀 Advanced EverMemOS Client Examples\n")
    
    try:
        example_usage()
        error_handling_example()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server.")
        print("Make sure the server is running at http://localhost:8000")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
