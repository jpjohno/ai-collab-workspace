import os
from github import Github, Auth
from openai import OpenAI

def main():
    print("🚀 Starting AI Collaboration Workspace Setup...")
    
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not GITHUB_TOKEN or not OPENAI_API_KEY or "your_actual" in GITHUB_TOKEN:
        print("\n❌ Error: Please make sure your real GITHUB_TOKEN and OPENAI_API_KEY are exported correctly.")
        return

    REPO_NAME = "ai-collab-workspace"
    
    print(f"Connecting to GitHub...")
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    user = g.get_user()
    
    try:
        repo = user.get_repo(REPO_NAME)
        print(f"📁 Found existing repository: {repo.full_name}")
    except Exception:
        print(f"📁 Creating new public repository: {REPO_NAME}...")
        repo = user.create_repo(
            name=REPO_NAME,
            description="Shared automated workspace for ChatGPT and Gemini collaboration.",
            private=False,
            auto_init=True
        )
        print(f"✨ Successfully created repository: {repo.full_name}")

    files_to_sync = {
        "README.md": "# AI Collaboration Workspace\nShared workspace for ChatGPT and Gemini to sync files and solve problems autonomously.",
        "shared_context.md": "# Shared Context & Memory Bank\n\n## Goal\nAutonomously debate and solve technical architecture problems.",
        "ai_debate_loop.py": '''import os
from openai import OpenAI

client = OpenAI()

def run_ai_debate(problem_statement: str, max_rounds: int = 2):
    print(f"\\n[Problem Statement]: {problem_statement}\\n" + "="*50)
    agent_a_system = "You are Agent Alpha: An analytical, cautious, and highly structural strategist."
    agent_b_system = "You are Agent Beta: An innovative, fast-moving, and pragmatic builder."

    history_a, history_b = [], []
    current_proposal = problem_statement

    for round_num in range(1, max_rounds + 1):
        print(f"--- Round {round_num} ---")
        prompt_a = f"Current plan/problem:\\n{current_proposal}\\n\\nProvide critique or improvements."
        res_a = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": agent_a_system}] + history_a + [{"role": "user", "content": prompt_a}])
        proposal_a = res_a.choices[0].message.content
        print(f"\\n[Agent Alpha]:\\n{proposal_a}\\n")
        
        history_a.append({"role": "user", "content": prompt_a})
        history_a.append({"role": "assistant", "content": proposal_a})

        prompt_b = f"Review Alpha's output:\\n{proposal_a}\\n\\nProvide a polished, actionable version."
        res_b = client.chat.completions.create(model="gpt-4o", messages=[{"role": "system", "content": agent_b_system}] + history_b + [{"role": "user", "content": prompt_b}])
        proposal_b = res_b.choices[0].message.content
        print(f"\\n[Agent Beta]:\\n{proposal_b}\\n")
        
        history_b.append({"role": "user", "content": prompt_b})
        history_b.append({"role": "assistant", "content": proposal_b})
        current_proposal = proposal_b

    print("="*50 + "\\n[Final Consensus]:\\n" + current_proposal)
    return current_proposal

if __name__ == "__main__":
    run_ai_debate("How can we streamline multi-agent file syncing via GitHub?", max_rounds=1)
'''
    }

    print("📦 Uploading workspace files to GitHub...")
    for file_path, content in files_to_sync.items():
        try:
            file_contents = repo.get_contents(file_path)
            repo.update_file(file_path, f"Update {file_path}", content, file_contents.sha)
        except Exception:
            repo.create_file(file_path, f"Add {file_path}", content)
        print(f"  -> Synced: {file_path}")

    print("\n🤖 Running live AI-to-AI test loop...")
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an AI collaborator."},
            {"role": "user", "content": "Say hello and confirm you are connected to the shared workspace framework."}
        ]
    )
    print(f"\n[Test Output from AI Model]:\n{response.choices[0].message.content}")
    print("\n✨ Done! Your GitHub repository is live and ready.")

if __name__ == "__main__":
    main()
