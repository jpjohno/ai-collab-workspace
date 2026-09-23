import os
from github import Github, Auth
from openai import OpenAI

def run_step():
    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("OPENAI_API_KEY")

    if not token or not api_key:
        print("❌ Missing GITHUB_TOKEN or OPENAI_API_KEY.")
        return

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_user().get_repo("ai-collab-workspace")
    client = OpenAI(api_key=api_key)

    context_file = repo.get_contents("shared_context.md")
    context = context_file.decoded_content.decode("utf-8")

    print("🤖 Agent Alpha (Architect): Drafting CapitalAPI and IGAPI client structure...")
    res_a = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Agent Alpha, a senior quant systems architect. Output only functional, production-ready Python code with complete class outlines and error handling."},
            {"role": "user", "content": f"Based on this project state:\n{context}\n\nWrite a unified Python module `trading_bridge.py` containing base structures for `CapitalAPI` and `IGAPI` that fetch market data, authenticate safely using environment variables, and log errors properly."}
        ]
    )
    code_proposal = res_a.choices[0].message.content

    print("🤖 Agent Beta (Security & Logic Auditor): Refining implementation...")
    res_b = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Agent Beta, an expert code reviewer. Clean and refine code to ensure strict security, non-blocking requests, and clean syntax. Output strictly raw Python code without Markdown wrappers."},
            {"role": "user", "content": f"Review and finalize this implementation:\n{code_proposal}"}
        ]
    )
    final_code = res_b.choices[0].message.content.strip()
    if final_code.startswith("```python"):
        final_code = final_code[9:]
    if final_code.startswith("```"):
        final_code = final_code[3:]
    if final_code.endswith("```"):
        final_code = final_code[:-3]
    final_code = final_code.strip()

    file_path = "trading_bridge.py"
    try:
        existing = repo.get_contents(file_path)
        repo.update_file(file_path, "Refactor trading_bridge.py via autonomous loop", final_code, existing.sha)
        print(f"✅ Updated {file_path} on GitHub.")
    except Exception:
        repo.create_file(file_path, "Add autonomous trading_bridge.py implementation", final_code)
        print(f"✨ Created {file_path} on GitHub.")

    status_update = context + f"\n\n## Autonomous Implementation Phase\nImplemented initial `trading_bridge.py` targeting Capital.com and IG.com integrations."
    repo.update_file("shared_context.md", "Log implementation milestone", status_update, context_file.sha)
    print("🚀 Repository updated successfully.")

if __name__ == "__main__":
    run_step()
