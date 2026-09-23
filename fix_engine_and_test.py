import subprocess
from github import Github, Auth
import os

def clean_code(raw: str) -> str:
    lines = raw.strip().splitlines()
    cleaned = [line for line in lines if not line.strip().startswith("```")]
    return "\n".join(cleaned).strip()

def run_fix():
    token = os.getenv("GITHUB_TOKEN")
    auth = Auth.Token(token) if token else None
    g = Github(auth=auth) if auth else None
    repo = g.get_user().get_repo("ai-collab-workspace") if g else None

    # 1. Clean arbitrage_engine.py
    with open("arbitrage_engine.py", "r", encoding="utf-8") as f:
        engine_code = clean_code(f.read())
    with open("arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(engine_code)

    if repo:
        try:
            f_obj = repo.get_contents("arbitrage_engine.py")
            repo.update_file("arbitrage_engine.py", "Fix syntax error in arbitrage_engine.py", engine_code, f_obj.sha)
            print("✅ Cleaned and updated arbitrage_engine.py on GitHub.")
        except Exception as e:
            print(f"GitHub notice (arbitrage_engine): {e}")

    # 2. Clean test_arbitrage_engine.py
    with open("test_arbitrage_engine.py", "r", encoding="utf-8") as f:
        test_code = clean_code(f.read())
    with open("test_arbitrage_engine.py", "w", encoding="utf-8") as f:
        f.write(test_code)

    if repo:
        try:
            t_obj = repo.get_contents("test_arbitrage_engine.py")
            repo.update_file("test_arbitrage_engine.py", "Clean test_arbitrage_engine.py", test_code, t_obj.sha)
            print("✅ Cleaned and updated test_arbitrage_engine.py on GitHub.")
        except Exception as e:
            print(f"GitHub notice (test_arbitrage_engine): {e}")

    # 3. Execute all unit tests
    print("\n🧪 Running full test suite...")
    res = subprocess.run(["python", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr)

if __name__ == "__main__":
    run_fix()
