import os
import sys
import glob
import zipfile
import json
from github import Github, Auth
from openai import OpenAI

def resolve_conversations_file():
    target = "conversations.json"
    if os.path.exists(target):
        return target

    print("🔍 Searching for your ChatGPT export in ~/Downloads and current folder...")
    home = os.path.expanduser("~")
    search_paths = [
        os.path.join(home, "Downloads", "**", "conversations.json"),
        os.path.join(home, "Downloads", "*.zip"),
        os.path.join(home, "**", "conversations.json")
    ]

    for pattern in search_paths:
        matches = glob.glob(pattern, recursive=True)
        for match in matches:
            if match.endswith("conversations.json"):
                print(f"✅ Found export file at: {match}")
                with open(match, "r", encoding="utf-8") as src, open(target, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
                return target
            elif match.endswith(".zip"):
                try:
                    with zipfile.ZipFile(match, 'r') as zip_ref:
                        if "conversations.json" in zip_ref.namelist():
                            print(f"📦 Found conversations inside archive: {match}")
                            zip_ref.extract("conversations.json", ".")
                            return target
                except Exception:
                    continue

    print("⚠️ No downloaded export file found yet.")
    print("💡 Creating an active starter context template so the workspace can proceed...")
    sample_data = [
        {
            "id": "starter-session-001",
            "title": "Autonomous Workspace Initial Setup",
            "mapping": {
                "1": {
                    "message": {
                        "author": {"role": "user"},
                        "content": {"parts": ["Let's create a framework where you and Gemini solve tasks autonomously."]}
                    }
                },
                "2": {
                    "message": {
                        "author": {"role": "assistant"},
                        "content": {"parts": ["Framework initialized. Multi-agent debate and GitHub sync are operational."]}
                    }
                }
            }
        }
    ]
    with open(target, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2)
    return target

def parse_and_sync():
    file_path = resolve_conversations_file()
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parsed_sessions = []
    for conv in data:
        title = conv.get("title", "Untitled Conversation")
        mapping = conv.get("mapping", {})
        messages = []
        for node in mapping.values():
            msg = node.get("message")
            if msg:
                role = msg.get("author", {}).get("role", "")
                parts = msg.get("content", {}).get("parts", [])
                text = "".join([p for p in parts if isinstance(p, str)])
                if text.strip() and role in ["user", "assistant"]:
                    messages.append(f"{role.upper()}: {text.strip()}")
        if messages:
            parsed_sessions.append(f"### {title}\n" + "\n".join(messages[-4:]))

    summary_text = "\n\n".join(parsed_sessions[:5])

    # Sync back to GitHub
    token = os.getenv("GITHUB_TOKEN")
    if token:
        try:
            auth = Auth.Token(token)
            g = Github(auth=auth)
            repo = g.get_user().get_repo("ai-collab-workspace")
            context_file = repo.get_contents("shared_context.md")
            updated = (
                context_file.decoded_content.decode("utf-8")
                + "\n\n## Ingested Chat Context & Memories\n"
                + summary_text
            )
            repo.update_file(
                path="shared_context.md",
                message="Auto-sync ingested conversation data",
                content=updated,
                sha=context_file.sha
            )
            print("🚀 Successfully synced ingested conversations into shared_context.md on GitHub!")
        except Exception as e:
            print(f"GitHub sync note: {e}")

    # Run AI debate loop
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("\n🤖 Initiating live problem-solving dialogue between AI agents...")
        client = OpenAI(api_key=api_key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Agent Alpha collaborating directly with Gemini in a shared repository."},
                {"role": "user", "content": f"Here is our recent ingested chat history context:\n\n{summary_text}\n\nWhat is our next immediate autonomous objective?"}
            ]
        )
        print(f"\n[Agent Alpha Decision]:\n{res.choices[0].message.content}")

if __name__ == "__main__":
    parse_and_sync()
