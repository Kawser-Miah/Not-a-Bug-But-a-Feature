#!/usr/bin/env python3
"""
Example usage of the Developer Guidance System API
"""

import requests
import json
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def example_workflow():
    """Example of the complete workflow"""
    
    print("🚀 Developer Guidance System - Example Workflow")
    print("=" * 50)
    
    # Step 1: Register a new user
    print("\n1️⃣ Registering a new user...")
    user_data = {
        "uuid": str(uuid.uuid4()),
        "name": "Alice Johnson",
        "username": "alice_dev",
        "age": 25,
        "time_duration": 90,  # 90 minutes per day
        "interests": ["frontend", "react", "javascript", "web development"]
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    if response.status_code == 200:
        user = response.json()
        user_id = user["id"]
        print(f"✅ User registered successfully! ID: {user_id}")
        print(f"   Name: {user['name']}")
        print(f"   Interests: {', '.join(user['interests'])}")
        print(f"   Time per day: {user['time_duration']} minutes")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # Step 2: Generate a roadmap
    print("\n2️⃣ Generating a personalized roadmap...")
    response = requests.post(f"{BASE_URL}/roadmap/generate", json={"user_id": user_id})
    if response.status_code == 200:
        roadmap = response.json()
        print(f"✅ Roadmap generated: {roadmap['title']}")
        print("   Steps:")
        for step in roadmap['steps']:
            print(f"   {step['step_num']}. {step['title']}")
    else:
        print(f"❌ Roadmap generation failed: {response.text}")
        return
    
    # Step 3: Generate tasks
    print("\n3️⃣ Generating daily tasks...")
    response = requests.post(f"{BASE_URL}/tasks/generate/{user_id}")
    if response.status_code == 200:
        tasks = response.json()["tasks"]
        print(f"✅ Generated {len(tasks)} tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"   {i}. {task['title']}")
            print(f"      Due: {task['assigned_time']}")
    else:
        print(f"❌ Task generation failed: {response.text}")
        return
    
    # Step 4: Simulate task completion
    print("\n4️⃣ Simulating task completion...")
    completed_tasks = [
        {"task_id": tasks[0]["id"], "completed": True},
        {"task_id": tasks[1]["id"] if len(tasks) > 1 else tasks[0]["id"], "completed": False}
    ]
    
    response = requests.post(f"{BASE_URL}/tasks/complete/{user_id}", json={"completed_tasks": completed_tasks})
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Task completion processed: {result['message']}")
    else:
        print(f"❌ Task completion failed: {response.text}")
    
    # Step 5: Simulate task failure
    print("\n5️⃣ Simulating task failure scenario...")
    failure_data = {
        "failure_reason": "I had unexpected work meetings and couldn't find time to complete the tasks. I need more guidance on how to approach these concepts.",
        "completed_tasks": [
            {"task_id": tasks[0]["id"], "completed": False},
            {"task_id": tasks[1]["id"] if len(tasks) > 1 else tasks[0]["id"], "completed": False}
        ]
    }
    
    response = requests.post(f"{BASE_URL}/tasks/failure/{user_id}", json=failure_data)
    if response.status_code == 200:
        reassigned_tasks = response.json()["tasks"]
        print(f"✅ Tasks reassigned with more guidance:")
        for i, task in enumerate(reassigned_tasks, 1):
            print(f"   {i}. {task['title']}")
            print(f"      New due date: {task['assigned_time']}")
    else:
        print(f"❌ Task failure handling failed: {response.text}")
    
    # Step 6: Get current tasks
    print("\n6️⃣ Getting current tasks...")
    response = requests.get(f"{BASE_URL}/tasks/{user_id}")
    if response.status_code == 200:
        current_tasks = response.json()["tasks"]
        print(f"✅ Current active tasks: {len(current_tasks)}")
        for task in current_tasks:
            status = "✅ Completed" if task['completed'] else "⏳ Pending"
            print(f"   {task['title']} - {status}")
    else:
        print(f"❌ Failed to get tasks: {response.text}")
    
    print("\n🎉 Example workflow completed!")
    print("\nTo continue using the system:")
    print("1. Complete tasks and use the completion endpoint")
    print("2. If you fail tasks, use the failure endpoint with explanations")
    print("3. The system will learn from your patterns and adapt")
    print("4. Use the regenerate roadmap endpoint to start fresh")

if __name__ == "__main__":
    try:
        example_workflow()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
