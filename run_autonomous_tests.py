import os
import subprocess
from github import Github, Auth
from openai import OpenAI

def main():
    token = os.getenv("GITHUB_TOKEN")
    api_key = os.getenv("OPENAI_API_KEY")

    if not token or not api_key:
        print("❌ Missing GITHUB_TOKEN or OPENAI_API_KEY.")
        return

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_user().get_repo("ai-collab-workspace")
    client = OpenAI(api_key=api_key)

    bridge_file = repo.get_contents("trading_bridge.py")
    bridge_code = bridge_file.decoded_content.decode("utf-8")

    print("🤖 Agent Alpha: Drafting unit test suite with mocks for trading_bridge.py...")
    res_a = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Agent Alpha. Write a standard Python unittest file using `unittest.mock` to test both CapitalAPI and IGAPI without making live network calls."},
            {"role": "user", "content": f"Here is trading_bridge.py:\n{bridge_code}\n\nWrite the complete test module `test_trading_bridge.py`."}
        ]
    )
    raw_test_code = res_a.choices[0].message.content

    print("🤖 Agent Beta: Auditing test coverage and syntax...")
    res_b = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are Agent Beta. Output strictly raw Python code for `test_trading_bridge.py` with zero Markdown wrappers or explanations."},
            {"role": "user", "content": f"Clean and finalize this test code:\n{raw_test_code}"}
        ]
    )
    test_code = res_b.choices[0].message.content.strip()
    if test_code.startswith("```python"):
        test_code = test_code[9:]
    if test_code.startswith("```"):
        test_code = test_code[3:]
    if test_code.endswith("```"):
        test_code = test_code[:-3]
    test_code = test_code.strip()

    # Save locally and push to GitHub
    with open("test_trading_bridge.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    try:
        existing = repo.get_contents("test_trading_bridge.py")
        repo.update_file("test_trading_bridge.py", "Update unit tests via autonomous loop", test_code, existing.sha)
        print("✅ Updated test_trading_bridge.py on GitHub.")
    except Exception:
        repo.create_file("test_trading_bridge.py", "Add autonomous unit tests", test_code)
        print("✨ Created test_trading_bridge.py on GitHub.")

    print("\n🧪 Executing test suite locally...")
    result = subprocess.run(["python", "-m", "unittest", "test_trading_bridge.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

if __name__ == "__main__":
    main()
