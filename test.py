from agents.planner_agent import PlannerAgent
import json
import os

def test_planner():
    planner = PlannerAgent()
    goal = "Build a shoe marketplace."
    subtasks = planner.plan(goal, metadata_file="plan.json")

    print("\n[*] Subtasks returned by planner:")
    for i, task in enumerate(subtasks, 1):
        print(f"{i}. {task}")

    # Verify the JSON content
    if os.path.exists("plan.json"):
        with open("plan.json", 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print("\n[*] JSON Metadata Loaded:")
        print(json.dumps(metadata, indent=4))
        
        # Check that key sections exist
        assert "planner" in metadata, "Missing 'planner' section in metadata"
        assert "coder" in metadata, "Missing 'coder' section in metadata"
        assert "goal" in metadata, "Missing 'goal' field in metadata"
        assert isinstance(metadata["planner"]["subtasks"], list), "'planner.subtasks' should be a list"
        print("[✓] JSON structure is valid.")
    else:
        print("[!] plan.json was not created.")

if __name__ == "__main__":
    test_planner()
