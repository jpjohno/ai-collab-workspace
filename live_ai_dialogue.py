import os
import json
from github import Github, Auth
from openai import OpenAI

def load_local_context():
    context = ""
    if os.path.exists("shared_context.md"):
        with open("shared_context.md", "r", encoding="utf-8") as f:
            context += "=== SHARED CONTEXT ===\n" + f.read() + "\n\n"

    # Direct target path avoiding recursive disk crawl
    known_path = "/Users/jamesjohnston/Downloads/a673c1ac949dbf59bd5542f2d898b4f44ba2701e89e21d44d85e1137a182247f-2023-10-11-16-08-31/conversations.json"
    target_file = known_path if os.path.exists(known_path) else ("conversations.json" if os.path.exists("conversations.json") else None)

    if target_file:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                recent_titles = [c.get("title", "") for c in data[:10] if c.get("title")]
                context += "=== RECENT CHATGPT TOPICS INGESTED ===\n" + ", ".join(recent_titles) + "\n\n"
        except Exception as e:
            context += f"=== CONVERSATION READ ERROR ===\n{e}\n\n"

    for module in ["trading_bridge.py", "arbitrage_engine.py"]:
        if os.path.exists(module):
            with open(module, "r", encoding="utf-8") as f:
                context += f"=== ACTIVE MODULE: {module} ===\n" + f.read()[:1500] + "\n\n"

    return context

def run_debate(turns=2):
    api_key = os.getenv("OPENAI_API_KEY")
    token = os.getenv("GITHUB_TOKEN")
    
    if not api_key:
        print("❌ OPENAI_API_KEY is missing from environment.")
        return

    client = OpenAI(api_key=api_key)
    print("⚡ Reading workspace and memory files instantly...")
    base_context = load_local_context()

    print("🧠 Workspace loaded. Initializing live AI-to-AI dialogue...\n")
    print("=" * 60)

    alpha_system = (
        "You are Agent Alpha (Lead Quant Architect & Strategy Lead). "
        "You have complete visibility over James's workspace and history. "
        "Discuss technical next steps directly with Agent Beta. "
        "Be sharp, technical, and concrete. If you need machine actions, files, or API credentials from James, state: '[REQUEST TO JAMES: ...]'."
    )

    beta_system = (
        "You are Agent Beta (Senior Systems Auditor & Security Engineer). "
        "You critique Agent Alpha's proposals, scrutinize execution risk (slippage, execution delay, rate limits), "
        "and enforce safe execution. Respond directly to Agent Alpha. "
        "If you need machine actions, files, or API credentials from James, state: '[REQUEST TO JAMES: ...]'."
    )

    current_prompt = (
        f"Project Context and Codebase State:\n{base_context}\n\n"
        "Agent Alpha, open the debate. What is the immediate technical hurdle in executing "
        "real trades between Capital.com and IG.com, and how do we resolve it now?"
    )

    dialogue_log = []

    for i in range(1, turns + 1):
        print(f"\n💬 [Turn {i} - Agent Alpha (Architect)] Thinking...")
        res_a = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": alpha_system},
                {"role": "user", "content": current_prompt}
            ]
        )
        alpha_msg = res_a.choices[0].message.content.strip()
        print(f"\nAgent Alpha:\n{alpha_msg}\n")
        dialogue_log.append(f"### Turn {i} - Agent Alpha\n{alpha_msg}\n")

        print(f"💬 [Turn {i} - Agent Beta (Auditor)] Counter-analyzing...")
        res_b = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": beta_system},
                {"role": "user", "content": f"Context:\n{base_context}\n\nAgent Alpha argued:\n{alpha_msg}\n\nEvaluate and rebut or refine."}
            ]
        )
        beta_msg = res_b.choices[0].message.content.strip()
        print(f"\nAgent Beta:\n{beta_msg}\n")
        dialogue_log.append(f"### Turn {i} - Agent Beta\n{beta_msg}\n")

        current_prompt = f"Agent Beta responded:\n{beta_msg}\n\nAgent Alpha, address this and advance the implementation."

    if token:
        try:
            auth = Auth.Token(token)
            g = Github(auth=auth)
            repo = g.get_user().get_repo("ai-collab-workspace")
            context_file = repo.get_contents("shared_context.md")
            updated = (
                context_file.decoded_content.decode("utf-8")
                + "\n\n## Live Multi-Turn Agent Debate Session\n"
                + "\n".join(dialogue_log)
            )
            repo.update_file(
                "shared_context.md",
                "Log live multi-turn AI debate session",
                updated,
                context_file.sha
            )
            print("\n💾 Complete debate transcript logged to shared_context.md on GitHub.")
        except Exception as e:
            print(f"GitHub sync note: {e}")

if __name__ == "__main__":
    run_debate(turns=2)
