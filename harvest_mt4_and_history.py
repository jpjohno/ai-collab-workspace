import os
import glob
import json
import re

def harvest_all():
    print("🔍 Hunting for MT4 source files, tick/bar data, and GitHub history...")
    
    mt4_records = []
    
    # 1. Search for MT4/MT5 files (.mq4, .mq5, .set, .csv)
    patterns = ["**/*.mq4", "**/*.mq5", "**/*.set", "**/*MT4*.csv", "../**/*.mq4", "../**/*.set"]
    found_files = []
    for pat in patterns:
        found_files.extend(glob.glob(pat, recursive=True))

    found_files = list(set(found_files))
    print(f"📂 Found {len(found_files)} MT4 strategy/configuration assets.")

    for fpath in found_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(4000) # Read the strategy header/logic
                mt4_records.append(f"### MT4 Asset: `{os.path.basename(fpath)}`\nPath: `{fpath}`\n```c\n{content}\n```")
        except Exception as e:
            print(f"⚠️ Note reading {fpath}: {e}")

    # 2. Search for all MT4 and strategy references inside project_knowledge_base.md
    extracted_chats = []
    if os.path.exists("project_knowledge_base.md"):
        with open("project_knowledge_base.md", "r", encoding="utf-8") as f:
            kb_text = f.read()

        # Extract sections specifically discussing MT4, MQL, or algorithmic execution
        chat_sections = kb_text.split("### Chat:")
        for section in chat_sections:
            if any(term in section.lower() for term in ["mt4", "mql", "metatrader", "expert advisor", "bridge", "latency"]):
                title = section.split("\n")[0].strip()
                extracted_chats.append(f"### Relevant Chat: {title}\n" + section[:3000])

        print(f"🧠 Extracted {len(extracted_chats)} discussions mentioning MT4 / algorithmic bridge logic.")

    # 3. Compile MT4 Strategy Dossier
    output_filename = "mt4_strategy_knowledge_base.md"
    with open(output_filename, "w", encoding="utf-8") as out:
        out.write("# WAYNE ENTERPRISES // MT4 & ALGORITHMIC STRATEGY DOSSIER\n\n")
        out.write("## 1. Discovered MetaTrader 4 / 5 Source Assets\n\n")
        out.write("\n\n---\n\n".join(mt4_records) if mt4_records else "No raw .mq4/.set files detected in immediate paths.\n")
        out.write("\n\n## 2. Ingested ChatGPT Historical Discussions on MT4 & Execution\n\n")
        out.write("\n\n---\n\n".join(extracted_chats) if extracted_chats else "No MT4 specific chat discussions flagged.\n")

    print(f"💾 Consolidated dossier saved to '{output_filename}'.")

if __name__ == "__main__":
    harvest_all()
