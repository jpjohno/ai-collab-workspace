import os
import sys
import json
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

def get_api_key():
    key_file = os.path.expanduser("~/.openai_key")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key and os.path.exists(key_file):
        try:
            with open(key_file, "r") as f:
                api_key = f.read().strip()
        except Exception:
            pass
            
    if not api_key:
        api_key = input("\nPaste your OpenAI API Key (sk-...) here: ").strip()
        if api_key:
            try:
                with open(key_file, "w") as f:
                    f.write(api_key)
            except Exception:
                pass
    return api_key

def read_docx(file_path):
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            texts = [node.text for node in tree.iter() if node.text]
            return " ".join(texts)
    except Exception:
        return ""

def read_pages(file_path):
    try:
        with zipfile.ZipFile(file_path) as z:
            for filename in z.namelist():
                if filename.startswith('index') or filename.endswith('.xml'):
                    xml_content = z.read(filename)
                    tree = ET.fromstring(xml_content)
                    texts = [node.text for node in tree.iter() if node.text]
                    return " ".join(texts)
    except Exception:
        return ""
    return ""

def parse_chatgpt_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        output = []
        for chat in data[:30]:
            title = chat.get('title', 'Untitled Chat')
            output.append(f"\n=== CHATGPT CONVERSATION: {title} ===")
            mapping = chat.get('mapping', {})
            for node in mapping.values():
                msg = node.get('message')
                if msg and msg.get('content') and msg['content'].get('parts'):
                    parts = msg['content']['parts']
                    text = " ".join([str(p) for p in parts if isinstance(p, str)])
                    if text.strip():
                        output.append(text[:400])
        return "\n".join(output)
    except Exception:
        return ""

def scan_folders(target_folders):
    combined_content = ""
    file_count = 0
    chatgpt_found = False
    skip_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv'}

    print("\nScanning directories for Junomo, Google Drive, and local files...")
    for scan_folder in target_folders:
        if not os.path.exists(scan_folder):
            continue
        for root, dirs, files in os.walk(scan_folder):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if file == "conversations.json":
                    print(f" -> Found ChatGPT Export: {file_path}")
                    chat_data = parse_chatgpt_json(file_path)
                    combined_content += f"\n--- CHATGPT EXPORT DATA ---\n{chat_data[:15000]}\n"
                    file_count += 1
                    chatgpt_found = True
                elif ext == ".docx":
                    text = read_docx(file_path)
                    if text:
                        combined_content += f"\n--- WORD FILE: {file} ---\n{text[:2500]}\n"
                        file_count += 1
                elif ext == ".pages":
                    text = read_pages(file_path)
                    if text:
                        combined_content += f"\n--- PAGES FILE: {file} ---\n{text[:2500]}\n"
                        file_count += 1
                elif ext in ('.txt', '.md', '.py', '.js', '.ts', '.json', '.html', '.htm', '.css', '.csv'):
                    if file != 'app.py' and not file.startswith('.'):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                text = f.read(2500)
                                if text.strip():
                                    combined_content += f"\n--- FILE: {file} ---\n{text}\n"
                                    file_count += 1
                        except Exception:
                            pass
                
                if len(combined_content) > 50000:
                    break
            if len(combined_content) > 50000:
                break

    return combined_content, file_count, chatgpt_found

def ask_openai(api_key, context, question):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are analyzing local project files, Word/Pages documents, Junomo workspace files, and Google Drive files."},
            {"role": "user", "content": f"Data collected:\n{context}\n\nUser Question: {question}"}
        ]
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['choices'][0]['message']['content']
    except Exception as e:
        return f"Error connecting to OpenAI: {e}"

def run():
    api_key = get_api_key()
    if not api_key:
        print("No API key provided. Exiting.")
        return

    home = os.path.expanduser("~")
    cloud_storage = os.path.join(home, "Library", "CloudStorage")
    
    print("\n========================================================")
    print("  ALL-IN-ONE SEARCH: JUNOMO, GOOGLE DRIVE & LOCAL FILES  ")
    print("========================================================")
    print("1. All Common Places (Downloads, Documents, Desktop & Google Drive) [RECOMMENDED]")
    print("2. Google Drive / Cloud Storage only")
    print("3. Enter Custom Path (e.g., Junomo folder)")

    choice = input("\nSelect option (1-3, or press Enter for All): ").strip()
    
    if choice == "2":
        folders = [cloud_storage]
    elif choice == "3":
        custom = input("Paste or type full folder path: ").strip()
        folders = [os.path.expanduser(custom)] if custom else [home]
    else:
        folders = [
            os.path.join(home, "Downloads"),
            os.path.join(home, "Documents"),
            os.path.join(home, "Desktop"),
            cloud_storage
        ]

    context, file_count, chatgpt_found = scan_folders(folders)
    
    if not context:
        print("No readable files found in those locations.")
        return

    print(f"Successfully loaded content from {file_count} files across your drives.")

    while True:
        question = input("\nWhat do you want to ask or search across these files? (Or type 'exit' to quit): ").strip()
        if not question:
            question = "Summarize all files, Junomo master workspace content, and strategy files."
        elif question.lower() in ['exit', 'quit', 'q']:
            print("\nExiting search app. Goodbye!")
            break

        print("\nAnalyzing with AI...")
        answer = ask_openai(api_key, context, question)
        
        print("\n---------------- SEARCH RESULTS ----------------")
        print(answer)
        print("------------------------------------------------\n")

if __name__ == "__main__":
    run()
