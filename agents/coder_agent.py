# agents/code_agent.py

import json
import os
from llama_cpp import Llama

class CoderAgent:
    def __init__(self, model_path="Models/phi-2/phi-2.Q5_K_M.gguf"):
        self.llm = Llama(model_path=model_path, n_ctx=2048)

    def read_plan(self, path="plan.json"):
        with open(path, 'r', encoding='utf-8') as f:
            plan = json.load(f)
        
        goal = plan.get("goal", "")
        subtasks = plan.get("subtasks", [])

        # Trim irrelevant content (e.g., OpenAI output trailing info)
        cleaned_subtasks = []
        for task in subtasks:
            if any(trigger in task.lower() for trigger in [
                "<|question_end|>", "question 1", "solution", "trello", "asana", "microsoft project"
            ]):
                break
            cleaned_subtasks.append(task)

        return {
            "goal": goal,
            "subtasks": cleaned_subtasks
        }


    def generate_code(self, goal: str, subtask: str) -> str:
        prompt = f"""You are a helpful coding assistant.

Project Goal: {goal}
Subtask: {subtask}

Generate the code for this subtask only. Keep it clean and readable.
Code:"""

        response = self.llm(prompt, max_tokens=800)
        return response["choices"][0]["text"].strip()

    def save_code_file(self, subtask: str, code: str, index: int):
        # Simple filetype routing
        if "<html>" in code.lower():
            ext = "html"
        elif "import" in code or "def " in code:
            ext = "py"
        elif "function" in code or "console.log" in code:
            ext = "js"
        elif "{" in code and ":" in code:
            ext = "css"
        else:
            ext = "txt"

        filename = f"task_{index+1}.{ext}"
        os.makedirs("project", exist_ok=True)
        with open(os.path.join("project", filename), "w", encoding='utf-8') as f:
            f.write(code)
        print(f"[✓] Saved {filename} for: {subtask}")

    def run(self):
        plan = self.read_plan()
        goal = plan.get("goal", "")
        subtasks = plan.get("subtasks", [])

        for i, subtask in enumerate(subtasks):
            print(f"\n[→] Working on subtask {i+1}: {subtask}")
            code = self.generate_code(goal, subtask)
            self.save_code_file(subtask, code, i)

