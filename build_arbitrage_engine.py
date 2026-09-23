import os
import subprocess
from github import Github, Auth
from openai import OpenAI

def run():
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

    # 1. Agent Alpha: Draft strategy engine
    print("🤖 Agent Alpha: Designing SpreadArbitrageEngine...")
    res_a = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a quantitative systems developer. Write clean, production-ready Python code for `arbitrage_engine.py`. It should take instances of CapitalAPI and IGAPI, fetch market data for a given instrument pair, calculate the bid/ask spread discrepancy, and evaluate whether an arbitrage opportunity exists exceeding a defined threshold. Return ONLY raw Python code."},
            {"role": "user", "content": "Write `arbitrage_engine.py` integrating with `trading_bridge.py`."}
        ]
    )
    engine_code = res_a.choices[0].message.content.strip()
    for fence in ["```python", "```"]:
        if engine_code.startswith(fence):
            engine_code = engine_code[len(fence):]
    if engine_code.endswith("```"):
        engine_code = engine_code[:-3]
    engine_code = engine_code.strip()

    with open("arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_code)

    try:
        f_obj = repo.get_contents("arbitrage_engine.py")
        repo.update_file("arbitrage_engine.py", "Update arbitrage engine", engine_code, f_obj.sha)
        print("✅ Updated arbitrage_engine.py on GitHub.")
    except Exception:
        repo.create_file("arbitrage_engine.py", "Add arbitrage engine", engine_code)
        print("✨ Created arbitrage_engine.py on GitHub.")

    # 2. Agent Beta: Draft and run tests for strategy engine
    print("🤖 Agent Beta: Building test suite for SpreadArbitrageEngine...")
    res_b = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a QA automation agent. Write a comprehensive unittest file `test_arbitrage_engine.py` using `unittest.mock` to verify the SpreadArbitrageEngine logic under positive spread, negative spread, and API exception scenarios. Return ONLY raw Python code."},
            {"role": "user", "content": f"Here is `arbitrage_engine.py`:\n{engine_code}\n\nGenerate `test_arbitrage_engine.py`."}
        ]
    )
    test_code = res_b.choices[0].message.content.strip()
    for fence in ["```python", "```"]:
        if test_code.startswith(fence):
            test_code = test_code[len(fence):]
    if test_code.endswith("```"):
        test_code = test_code[:-3]
    test_code = test_code.strip()

    with open("test_arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    try:
        t_obj = repo.get_contents("test_arbitrage_engine.py")
        repo.update_file("test_arbitrage_engine.py", "Update engine tests", test_code, t_obj.sha)
        print("✅ Updated test_arbitrage_engine.py on GitHub.")
    except Exception:
        repo.create_file("test_arbitrage_engine.py", "Add engine tests", test_code)
        print("✨ Created test_arbitrage_engine.py on GitHub.")

    # Update CI workflow to test all test suites
    ci_path = ".github/workflows/ci.yml"
    ci_file = repo.get_contents(ci_path)
    updated_ci = ci_file.decoded_content.decode("utf-8").replace(
        "python -m unittest test_trading_bridge.py",
        "python -m unittest discover -s . -p 'test_*.py'"
    )
    repo.update_file(ci_path, "Run all unit tests via discover in CI", updated_ci, ci_file.sha)
    print("✅ Updated CI workflow to auto-discover all test files.")

    # Run tests locally
    print("\n🧪 Executing full test discovery locally...")
    test_run = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
    print(test_run.stdout)
    if test_run.stderr:
        print(test_run.stderr)

if __name__ == "__main__":
    run()
