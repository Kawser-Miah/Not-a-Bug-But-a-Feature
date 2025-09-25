from typing import List, Dict, Any
import requests
import json

class SourcesAPIService:
    """Service to handle calling external sources API"""
    
    def __init__(self, api_url: str = None):
        # You can set this via environment variable or pass it directly
        self.sources_api_url = api_url or "http://localhost:9000/get-sources"  # Replace with your actual URL
    
    def fetch_sources_for_tasks(self, tasks_data: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """
        Call external API to get sources for tasks
        Args:
            tasks_data: List of {id: int, title: str, description: str}
        Returns:
            Dict mapping task_id to list of sources
        """
        try:
            # Prepare the payload
            payload = [
                {
                    "id": task["id"],
                    "title": task["title"],
                    "description": task["description"]
                }
                for task in tasks_data
            ]
            
            print(f"Calling sources API at {self.sources_api_url} with {len(payload)} tasks")
            
            # Make API call
            response = requests.post(
                self.sources_api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                sources_response = response.json()
                # Convert to dict for easy lookup: {id: [sources]}
                sources_dict = {item["id"]: item["sources"] for item in sources_response}
                print(f"Successfully received sources for {len(sources_dict)} tasks")
                return sources_dict
            else:
                print(f"Sources API returned status {response.status_code}: {response.text}")
                return {}
        except requests.exceptions.Timeout:
            print("Sources API call timed out")
            return {}
        except requests.exceptions.ConnectionError:
            print("Could not connect to sources API")
            return {}
        except Exception as e:
            print(f"Error calling sources API: {e}")
            return {}

# Mock implementation for testing purposes
class MockSourcesAPIService:
    """Mock service that returns dummy sources for testing"""
    
    def fetch_sources_for_tasks(self, tasks_data: List[Dict[str, Any]]) -> Dict[int, List[str]]:
        """Mock implementation that returns sample sources"""
        sources_dict = {}
        for task in tasks_data:
            # Generate mock sources based on task content
            sources_dict[task["id"]] = [
                f"https://docs.example.com/{task['title'].lower().replace(' ', '-')}",
                f"https://tutorial.com/{task['title'][:10].lower()}",
                f"https://reference.com/api/{task['id']}"
            ]
        print(f"Mock: Generated sources for {len(sources_dict)} tasks")
        return sources_dict