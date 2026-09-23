import os
from github import Github, Auth

def setup_github_ci():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Missing GITHUB_TOKEN.")
        return

    auth = Auth.Token(token)
    g = Github(auth=auth)
    repo = g.get_user().get_repo("ai-collab-workspace")

    ci_workflow_content = """name: Automated Tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Check out repository
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests PyGithub openai

    - name: Run Unit Tests
      run: |
        python -m unittest test_trading_bridge.py
"""

    workflow_path = ".github/workflows/ci.yml"

    try:
        existing = repo.get_contents(workflow_path)
        repo.update_file(workflow_path, "Update automated CI test workflow", ci_workflow_content, existing.sha)
        print("✅ Updated CI workflow on GitHub.")
    except Exception:
        repo.create_file(workflow_path, "Add automated CI test workflow", ci_workflow_content)
        print("✨ Created .github/workflows/ci.yml on GitHub.")

    print("🚀 Continuous Integration active! GitHub will now verify your tests on every push.")

if __name__ == "__main__":
    setup_github_ci()
