import os
from github import Github, Auth
from openai import OpenAI

def main():
    print("🔄 Connecting to GitHub workspace...")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not GITHUB_TOKEN or not OPENAI_API_KEY:
        print("❌ Missing tokens! Make sure GITHUB_TOKEN and OPENAI_API_KEY are set.")
        return

    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
    user = g.get_user()
    repo = user.get_repo("ai-collab-workspace")

    # 1. Pull current shared context from GitHub
    try:
        context_file = repo.get_contents("shared_context.md")
        current_context = context_file.decoded_content.decode("utf-8")
        print("📖 Successfully read shared_context.md from GitHub.")
    except Exception as e:
        print(f"⚠️ Could not read shared_context.md: {e}")
        current_context = "Initial context."

    # 2. Run an AI debate session on a current objective
    print("🤖 Running AI consensus loop...")
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = (
        f"Based on our shared workspace context:\n{current_context}\n\n"
        "What is the next best technical step to build a seamless memory-import bridge "
        "from ChatGPT exports into our Python workspace? Provide a concise, highly actionable solution."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert AI software architect collaborating in an automated workspace."},
            {"role": "user", "content": prompt}
        ]
    )
    
    consensus_result = response.choices[0].message.content
    print(f"\n[AI Consensus Result]:\n{consensus_result}\n")

    # 3. Update shared_context.md on GitHub with the new findings
    updated_context = current_context + f"\n\n## Update / Consensus\n{consensus_result}"
    
    repo.update_file(
        path="shared_context.md",
        message="Update shared context via automated AI loop",
        content=updated_context,
        sha=context_file.sha
    )
    print("✨ Successfully pushed updated consensus back to GitHub repository!")

if __name__ == "__main__":
    main()
