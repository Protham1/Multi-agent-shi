# test_planner_and_coder.py

from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent

def main():
    planner = PlannerAgent()
    goal = "Build a weather forecast web app using an API."
    subtasks = planner.plan(goal)

    # Now start coding phase
    coder = CoderAgent()
    coder.run()

if __name__ == "__main__":
    main()
