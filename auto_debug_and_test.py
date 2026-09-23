import os
import subprocess
from github import Github, Auth
from openai import OpenAI

def run_pipeline():
    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("OPENAI_API_KEY")

    if not token or not api_key:
        print("❌ Missing credentials.")
        return

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_user().get_repo("ai-collab-workspace")
    client = OpenAI(api_key=api_key)

    # 1. Sync trading_bridge.py locally from GitHub
    print("📥 Syncing trading_bridge.py locally from GitHub...")
    bridge_file = repo.get_contents("trading_bridge.py")
    bridge_code = bridge_file.decoded_content.decode("utf-8")
    with open("trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(bridge_code)

    # 2. Sync test_trading_bridge.py locally from GitHub
    test_file = repo.get_contents("test_trading_bridge.py")
    test_code = test_file.decoded_content.decode("utf-8")
    with open("test_trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    # 3. Execute tests
    print("🧪 Running unit test suite...")
    res = subprocess.run(["python", "-m", "unittest", "test_trading_bridge.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

    # 4. Autonomous repair loop if failures occur
    if res.returncode != 0:
        print("⚠️ Tests failed. Agent Alpha & Beta initiating autonomous repair loop...")
        prompt = (
            f"Here is `trading_bridge.py`:\n{bridge_code}\n\n"
            f"Here is `test_trading_bridge.py`:\n{test_code}\n\n"
            f"Execution failed with error:\n{res.stderr}\n\n"
            "Diagnose the failure and return strictly corrected, complete Python code for `trading_bridge.py`."
        )
        fix_res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a senior debugging agent. Return strictly executable Python code without Markdown formatting."},
                {"role": "user", "content": prompt}
            ]
        )
        patched = fix_res.choices[0].message.content.strip()
        for fence in ["```python", "```"]:
            if patched.startswith(fence):
                patched = patched[len(fence):]
        if patched.endswith("```"):
            patched = patched[:-3]
        patched = patched.strip()

        with open("trading_bridge.py", "w", encoding="utf-8") as f:
            f.write(patched)

        repo.update_file("trading_bridge.py", "Autonomous bugfix based on test trace", patched, bridge_file.sha)
        print("✅ Patched code pushed to GitHub. Re-running tests...")
        retry = subprocess.run(["python", "-m", "unittest", "test_trading_bridge.py"], capture_output=True, text=True)
        print(retry.stdout)
        if retry.stderr:
            print(retry.stderr)
    else:
        print("🎉 All autonomous tests passed successfully!")

if __name__ == "__main__":
    run_pipeline()
