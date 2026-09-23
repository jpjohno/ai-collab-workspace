import os
import glob
import json
from github import Github

def sync_knowledge():
    print("🔍 Searching for past ChatGPT exports and workspace files...")
    
    knowledge_sections = []
    
    # 1. Look for ChatGPT conversations.json exports
    export_files = (
        glob.glob("conversations.json") + 
        glob.glob("**/conversations.json", recursive=True) +
        glob.glob("../conversations.json")
    )
    
    if export_files:
        chosen_file = export_files[0]
        print(f"📖 Found ChatGPT export at: {chosen_file}")
        try:
            with open(chosen_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            chat_logs = []
            for conv in data[:15]: # Process up to 15 recent conversations
                title = conv.get("title", "Untitled")
                mapping = conv.get("mapping", {})
                convo_text = []
                for node_id, node in mapping.items():
                    msg = node.get("message")
                    if msg and msg.get("content") and msg["content"].get("parts"):
                        role = msg.get("author", {}).get("role", "unknown")
                        parts = [str(p) for p in msg["content"]["parts"] if isinstance(p, str)]
                        text = "\n".join(parts).strip()
                        if text:
                            convo_text.append(f"**{role.upper()}**: {text}")
                if convo_text:
                    chat_logs.append(f"### Chat: {title}\n" + "\n\n".join(convo_text[-6:])) # Last few turns
            
            knowledge_sections.append("## Past ChatGPT Design Decisions\n" + "\n\n---\n\n".join(chat_logs))
            print(f"✅ Ingested {len(chat_logs)} chat threads from export.")
        except Exception as e:
            print(f"⚠️ Note parsing conversations.json: {e}")
    else:
        print("ℹ️ No conversations.json found locally. (Drop it into ~/trading_workspace anytime to parse)")

    # 2. Pull down shared_context.md from GitHub
    token = os.getenv("GITHUB_TOKEN")
    if token:
        try:
            g = Github(token)
            repo = g.get_user().get_repo("ai-collab-workspace")
            context_file = repo.get_contents("shared_context.md")
            github_context = context_file.decoded_content.decode("utf-8")
            knowledge_sections.append("## GitHub Shared Context & Agent Debates\n" + github_context)
            print("✅ Successfully pulled remote shared_context.md from GitHub.")
        except Exception as e:
            print(f"⚠️ GitHub sync note: {e}")

    # 3. Write compiled knowledge base
    output_filename = "project_knowledge_base.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("# Consolidated Multi-Agent Knowledge Base\n\n" + "\n\n".join(knowledge_sections))

    print(f"💾 Central knowledge compiled into '{output_filename}'.")

if __name__ == "__main__":
    sync_knowledge()
