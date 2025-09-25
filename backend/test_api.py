#!/usr/bin/env python3
"""
Simple test script to verify the API endpoints work correctly
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def test_user_registration():
    """Test user registration"""
    print("Testing user registration...")
    
    user_data = {
        "uuid": str(uuid.uuid4()),
        "name": "John Doe",
        "username": "johndoe",
        "age": 23,
        "time_duration": 60,
        "interests": ["backend", "docker", "python"]
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()["id"]
    return None

def test_roadmap_generation(user_id):
    """Test roadmap generation"""
    print(f"\nTesting roadmap generation for user {user_id}...")
    
    response = requests.post(f"{BASE_URL}/roadmap/generate", json={"user_id": user_id})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_task_generation(user_id):
    """Test task generation"""
    print(f"\nTesting task generation for user {user_id}...")
    
    response = requests.post(f"{BASE_URL}/tasks/generate/{user_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        return response.json()["tasks"]
    return []

def test_task_completion(user_id, tasks):
    """Test task completion"""
    print(f"\nTesting task completion for user {user_id}...")
    
    # Complete first task
    completed_tasks = [
        {"task_id": tasks[0]["id"], "completed": True},
        {"task_id": tasks[1]["id"] if len(tasks) > 1 else tasks[0]["id"], "completed": False}
    ]
    
    response = requests.post(f"{BASE_URL}/tasks/complete/{user_id}", json={"completed_tasks": completed_tasks})
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def test_task_failure(user_id, tasks):
    """Test task failure handling"""
    print(f"\nTesting task failure for user {user_id}...")
    
    # Simulate failure
    completed_tasks = [
        {"task_id": tasks[0]["id"], "completed": False},
        {"task_id": tasks[1]["id"] if len(tasks) > 1 else tasks[0]["id"], "completed": False}
    ]
    
    failure_data = {
        "failure_reason": "I didn't have enough time to complete the tasks due to work commitments",
        "completed_tasks": completed_tasks
    }
    
    response = requests.post(f"{BASE_URL}/tasks/failure/{user_id}", json=failure_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    """Run all tests"""
    print("Starting API tests...")
    
    try:
        # Test user registration
        user_id = test_user_registration()
        if not user_id:
            print("User registration failed!")
            return
        
        # Test roadmap generation
        if not test_roadmap_generation(user_id):
            print("Roadmap generation failed!")
            return
        
        # Test task generation
        tasks = test_task_generation(user_id)
        if not tasks:
            print("Task generation failed!")
            return
        
        # Test task completion
        test_task_completion(user_id, tasks)
        
        # Test task failure
        test_task_failure(user_id, tasks)
        
        print("\nAll tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
