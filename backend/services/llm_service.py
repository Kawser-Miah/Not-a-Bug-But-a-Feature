from langchain_groq import ChatGroq
from config import llm
from typing import List, Dict, Any, Any
import json
import re
from datetime import datetime, timedelta

class LLMService:
    def __init__(self):
        self.llm = llm
    
    def _extract_json_block(self, content: str) -> str:
        """Extract a balanced JSON object from the response, stripping code fences.
        If no object is found, attempt to extract a tasks array and wrap it.
        """
        # Remove code fences
        content = re.sub(r"```(?:json)?\s*|```", "", content, flags=re.IGNORECASE)
        content = content.strip()
        # Try full JSON object first
        start_idx = content.find('{')
        if start_idx != -1:
            depth = 0
            end_idx = -1
            for i in range(start_idx, len(content)):
                ch = content[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            if end_idx != -1:
                return content[start_idx:end_idx + 1]
            last = content.rfind('}')
            if last != -1:
                return content[start_idx:last + 1]
        # Fallback: try to find a tasks array and wrap it
        tasks_key_idx = content.lower().find('"tasks"')
        if tasks_key_idx == -1:
            raise ValueError("No JSON object start found")
        bracket_idx = content.find('[', tasks_key_idx)
        if bracket_idx == -1:
            raise ValueError("No tasks array found")
        depth = 0
        end_idx = -1
        for i in range(bracket_idx, len(content)):
            ch = content[i]
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    end_idx = i
                    break
        if end_idx == -1:
            raise ValueError("Unbalanced tasks array")
        tasks_array = content[bracket_idx:end_idx + 1]
        return '{"tasks": ' + tasks_array + '}'

    def _safe_json_loads(self, text: str) -> Any:
        """Parse JSON, repairing common issues like unescaped backslashes and newlines."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Escape lone backslashes not part of valid escapes
            repaired = re.sub(r"(?<!\\)\\(?![\\/\"bnrtfu])", r"\\\\", text)
            # Collapse excessive whitespace/newlines in strings
            repaired = re.sub(r"\s+", " ", repaired)
            return json.loads(repaired)
    
    def generate_roadmap(self, user_interests: List[str], time_duration: int, age: int) -> Dict[str, Any]:
        """Generate a personalized roadmap based on user interests and time constraints"""
        
        prompt = f"""
        Create a comprehensive learning roadmap for a {age}-year-old developer who wants to learn about: {', '.join(user_interests)}.
        
        They can spend {time_duration} minutes per day learning.
        
        Generate a roadmap with 10-13 steps that are:
        1. Progressive (each step builds on the previous)
        2. Realistic for the time commitment
        3. Practical and hands-on
        4. Specific to their interests
        
        Return the response in this exact JSON format:
        {{
            "title": "Your Roadmap Title",
            "steps": [
                {{"step_num": 1, "title": "Step 1 Title"}},
                {{"step_num": 2, "title": "Step 2 Title"}},
                ...
            ]
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            json_str = self._extract_json_block(content)
            roadmap_data = self._safe_json_loads(json_str)
            return roadmap_data
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            # Fallback roadmap if LLM fails
            return {
                "title": f"Learning Path for {', '.join(user_interests[:2])}",
                "steps": [
                    {"step_num": 1, "title": "Learn the Basics"},
                    {"step_num": 2, "title": "Practice with Projects"},
                    {"step_num": 3, "title": "Build Real Applications"},
                    {"step_num": 4, "title": "Advanced Concepts"},
                    {"step_num": 5, "title": "Portfolio Development"}
                ]
            }
    
    def generate_tasks(self, roadmap_step: str, user_interests: List[str], time_duration: int,
                      previous_failures: List[str] = None,
                      all_steps: List[Dict[str, Any]] = None,
                      current_step_num: int = 1) -> List[Dict[str, Any]]:
        """Generate 3-5 tasks for a specific roadmap step. LLM is constrained to current step."""
        
        failure_context = ""
        if previous_failures:
            failure_context = f"""
            Previous challenges the user faced:
            {'. '.join(previous_failures[-3:])}  # Last 3 failures
            
            Consider these challenges when creating tasks and make them more detailed and supportive.
            """
        
        steps_context = ""
        if all_steps:
            steps_lines = [f"Step {s.get('step_num')}: {s.get('title')}" for s in all_steps if isinstance(s, dict)]
            steps_context = "\n".join(steps_lines)

        prompt = f"""
        You are generating tasks ONLY for the current roadmap step.
        
        Roadmap Steps:\n{steps_context}
        Current Step Number: {current_step_num}
        Current Step Title: "{roadmap_step}"
        
        STRICT REQUIREMENTS:
        - The tasks must be exclusively about the CURRENT STEP. Do NOT introduce topics from future steps.
        - If the roadmap includes topics like RAG, LLMs, or deployment in later steps, DO NOT mention them now unless they are part of the current step.
        
        Create 3-5 practical, hands-on tasks for this specific step.
        
        User interests: {', '.join(user_interests)}
        Daily time available: {time_duration} minutes
        
        {failure_context}
        
        Each task should be:
        1. Specific and actionable
        2. Beginner-friendly, assume the user is a novice for this step
        3. Appropriate for the time commitment
        4. Include clear instructions and hints
        5. Include expected outcomes
        6. Description MUST be a single paragraph (no newlines, no markdown, no lists, no code blocks)
        7. Include a "sources" field as a list of URLs or resource names relevant to the task.
        8. Do NOT include markdown code fences or unescaped backslashes.
        
        Return tasks in this exact JSON format (ONLY valid JSON, no extra text):
        {{
            "tasks": [
                {{
                    "title": "Task Title",
                    "description": "Detailed description with clear steps and expected outcome",
                    "sources": ["https://resource1.com", "https://resource2.com"]
                }}
            ]
        }}
        """
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content
            print("--------------------------------")
            print(f"Tasks from LLM: \n{content}")
            print("--------------------------------")
            json_str = self._extract_json_block(content)
            tasks_data = self._safe_json_loads(json_str)
            return tasks_data.get("tasks", [])
        except Exception as e:
            print(f"Error generating tasks: {e}")
            # Fallback tasks if LLM fails
            return [
                {
                    "title": f"Practice {roadmap_step} Basics",
                    "description": f"Spend {time_duration//2} minutes exploring the fundamentals of {roadmap_step}. Try to understand the core concepts and write down any questions you have.",
                    "sources": []
                },
                {
                    "title": f"Hands-on {roadmap_step} Exercise",
                    "description": f"Complete a practical exercise related to {roadmap_step}. Follow a tutorial or create a simple project that demonstrates your understanding.",
                    "sources": []
                },
                {
                    "title": f"Reflect on {roadmap_step} Learning",
                    "description": f"Take {time_duration//4} minutes to reflect on what you learned. Write down key takeaways and plan your next steps.",
                    "sources": []
                }
            ]
    
    def reassign_tasks(self, incomplete_tasks: List[Dict], failure_reason: str, 
                        user_interests: List[str], time_duration: int, 
                        previous_failures: List[str] = None) -> List[Dict[str, Any]]:
            """Reassign tasks based on failure reason and previous failures"""
            
            failure_context = ""
            if previous_failures:
                failure_context = f"""
                User's previous challenges:
                {'. '.join(previous_failures[-5:])}  # Last 5 failures
                """
            
            incomplete_tasks_str = "\n".join([f"- {task['title']}: {task['description']}" for task in incomplete_tasks])
            
            prompt = f"""
            The user failed to complete some tasks and provided this reason: "{failure_reason}"
            
            Incomplete tasks:
            {incomplete_tasks_str}
            
            User interests: {', '.join(user_interests)}
            Daily time available: {time_duration} minutes
            
            {failure_context}
            
            Based on the failure reason, reassign the incomplete tasks with:
            1. More detailed descriptions and step-by-step guidance
            2. Additional supportive resources or hints
            3. Break down complex tasks into smaller, manageable parts
            4. Address the specific challenges mentioned in the failure reason
            5. The description MUST be a single paragraph (no newlines, no markdown, no lists, no code blocks)
            6. Include a "sources" field as a list of URLs or resource names relevant to the task.
            
            You may also add 1-2 new related tasks if appropriate, but keep total tasks between 3-5.
            
            Return tasks in this exact JSON format:
            {{
                "tasks": [
                    {{
                        "title": "Updated Task Title",
                        "description": "More detailed and supportive description with clear steps",
                        "sources": ["https://resource1.com", "https://resource2.com"]
                    }},
                    ...
                ]
            }}
            """
            
            try:
                response = self.llm.invoke(prompt)
                content = response.content
                json_str = self._extract_json_block(content)
                tasks_data = self._safe_json_loads(json_str)
                return tasks_data.get("tasks", [])
            except Exception as e:
                # Fallback: return original tasks with more detail
                return [
                    {
                        "title": f"Reassigned: {task['title']}",
                        "description": f"Let's break this down into smaller steps. {task['description']} Additional guidance: Take your time and don't hesitate to ask for help if needed.",
                        "sources": []
                    }
                    for task in incomplete_tasks[:3]
                ]
