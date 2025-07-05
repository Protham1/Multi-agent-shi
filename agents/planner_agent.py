import json
from datetime import datetime
import google.generativeai as genai

class PlannerAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-pro")

    def plan(self, user_goal: str, metadata_file: str = "plan.json") -> list:
        prompt = f"""
You are a multi-agent project planner. Given a software goal, return a structured JSON with detailed plans for planner, coder, and designer agents.

The JSON should contain:
- planner: specific subtasks and requirements
- coder: coding tasks, technical specs, and file_structure
- designer: theme, UI components, pages, and design system

EXAMPLE:
Goal: Build a weather app
Output:
{{
  "goal": "Build a weather app",
  "project_type": "web_application",
  "domain": "weather",
  "planner": {{
    "subtasks": [
      "Define app requirements",
      "Research weather APIs",
      "Plan architecture",
      "Create timeline"
    ],
    "requirements": {{
      "core_features": ["Current weather", "Forecast", "Search"],
      "tech_stack": "React + OpenWeatherMap",
      "timeline": "2 weeks"
    }}
  }},
  "coder": {{
    "tasks": [
      "Setup React project",
      "Create API service",
      "Build UI components"
    ],
    "technical_specs": {{
      "frontend": "React",
      "backend": "Node",
      "database": "None",
      "deployment": "Vercel"
    }},
    "file_structure": {{
      "src/App.js": "Main component",
      "src/api/weather.js": "API handler"
    }}
  }},
  "designer": {{
    "theme": "Blue card UI with icons",
    "pages": [
      {{"name": "Home", "components": ["Search", "Forecast cards"]}}
    ],
    "design_system": {{
      "colors": {{"primary": "#2196F3"}},
      "typography": {{"headings": "Inter", "body": "Sans"}}
    }}
  }}
}}

NOW DO THIS:
Goal: {user_goal}
Output:
"""

        print("[*] Sending request to Gemini Pro...")
        response = self.model.generate_content(prompt)
        output = response.text.strip()

        try:
            parsed_json = json.loads(output)
            parsed_json["generated_at"] = datetime.now().isoformat()
        except json.JSONDecodeError as e:
            print(f"[!] JSON decode error: {e}")
            print(f"[!] Raw output was:\n{output}")
            return []

        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_json, f, indent=4)

        print(f"[✓] Plan saved to {metadata_file}")
        return parsed_json.get("planner", {}).get("subtasks", [])

# Example usage
if __name__ == "__main__":
    gemini_api_key = "AIzaSyCjz9FOaa6SlZjC_gxPocXi0k0LB4KEoF8"  # Replace with your real Gemini API key
    planner = PlannerAgent(api_key=gemini_api_key)
    
    goal = "Build a social media platform for animals"
    planner.plan(goal)
