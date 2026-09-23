import os
import json
import subprocess
from typing import List, Dict, Any
from github import Github, Auth
from openai import OpenAI

class SharedMemory:
    """Manages context persistence locally and on GitHub."""
    def __init__(self, repo_name="jpjohno/ai-collab-workspace"):
        self.repo_name = repo_name
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = None
        if self.token:
            try:
                auth = Auth.Token(self.token)
                self.repo = Github(auth=auth).get_user().get_repo("ai-collab-workspace")
            except Exception as e:
                print(f"⚠️ GitHub sync offline: {e}")

    def read_context(self) -> str:
        if os.path.exists("shared_context.md"):
            with open("shared_context.md", "r", encoding="utf-8") as f:
                return f.read()
        return "No prior shared context found."

    def append_log(self, title: str, content: str):
        with open("shared_context.md", "a", encoding="utf-8") as f:
            f.write(f"\n\n## {title}\n{content}\n")
        
        if self.repo:
            try:
                context_file = self.repo.get_contents("shared_context.md")
                updated = context_file.decoded_content.decode("utf-8") + f"\n\n## {title}\n{content}\n"
                self.repo.update_file("shared_context.md", f"Log: {title}", updated, context_file.sha)
                print("💾 Synced update to GitHub repository.")
            except Exception as e:
                print(f"GitHub push failed: {e}")

class ToolRegistry:
    """Executes actions approved by the agents and user."""
    @staticmethod
    def execute_terminal(command: str) -> Dict[str, Any]:
        """Runs a safe shell command on the host machine."""
        print(f"\n⚙️ [Tool: Executing Terminal Command]: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode
        }

class AgentSession:
    """Configurable multi-agent debate and problem solver."""
    def __init__(self, objective: str, domain_context: str = ""):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=self.api_key)
        self.memory = SharedMemory()
        self.objective = objective
        self.domain_context = domain_context

    def run_mission(self, turns: int = 2):
        print(f"🎯 Mission Objective: {self.objective}\n")
        history_context = self.memory.read_context()

        alpha_system = (
            "You are Agent Alpha (Lead Strategist & Architect). "
            "You design step-by-step technical blueprints to solve the objective. "
            "If code or actions need execution, format them clearly. "
            "If you need terminal actions or keys from James, output: '[REQUEST TO JAMES: ...]'"
        )

        beta_system = (
            "You are Agent Beta (Auditor, Security & Implementation Specialist). "
            "You rigorously check Alpha's plans for flaws, failure modes, security gaps, and edge cases. "
            "Provide concrete counter-proposals or finalized implementation fixes."
        )

        current_prompt = (
            f"=== CURRENT MISSION ===\n{self.objective}\n\n"
            f"=== EXTRA DOMAIN CONTEXT ===\n{self.domain_context}\n\n"
            f"=== SHARED REPOSITORY HISTORY ===\n{history_context[-2000:]}\n\n"
            "Agent Alpha, open with your architectural plan to solve this objective."
        )

        session_log = []

        for i in range(1, turns + 1):
            print(f"\n💬 [Turn {i} - Agent Alpha (Architect)] Thinking...")
            res_a = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": alpha_system},
                    {"role": "user", "content": current_prompt}
                ]
            )
            msg_a = res_a.choices[0].message.content.strip()
            print(f"\nAgent Alpha:\n{msg_a}\n")
            session_log.append(f"### Turn {i} - Alpha\n{msg_a}")

            print(f"💬 [Turn {i} - Agent Beta (Auditor)] Scrutinizing...")
            res_b = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": beta_system},
                    {"role": "user", "content": f"Objective: {self.objective}\n\nAlpha proposed:\n{msg_a}\n\nCritique, refine, or validate."}
                ]
            )
            msg_b = res_b.choices[0].message.content.strip()
            print(f"\nAgent Beta:\n{msg_b}\n")
            session_log.append(f"### Turn {i} - Beta\n{msg_b}")

            current_prompt = f"Agent Beta responded:\n{msg_b}\n\nAgent Alpha, adjust the plan and take the next step."

        # Save session to persistent store
        self.memory.append_log(f"Mission: {self.objective[:50]}", "\n\n".join(session_log))

if __name__ == "__main__":
    import sys
    # Example flexible trigger: specify whatever objective you want
    goal = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Design a multi-tool agent framework that can run shell commands, analyze files, and build any Python application."
    session = AgentSession(objective=goal)
    session.run_mission(turns=2)
