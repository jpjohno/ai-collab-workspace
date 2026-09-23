import json
import os

def parse_chatgpt_conversations(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Error: Could not find file at {file_path}")
        print("Make sure you have extracted your ChatGPT export and placed 'conversations.json' in this folder.")
        return None

    print(f"📂 Reading ChatGPT export from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Error: The file is not a valid JSON document.")
            return None

    parsed_sessions = []
    
    # ChatGPT export structure contains a list of conversation dictionaries
    for conv in data:
        title = conv.get("title", "Untitled Conversation")
        conv_id = conv.get("id", "unknown_id")
        mapping = conv.get("mapping", {})
        
        messages = []
        for node_id, node_data in mapping.items():
            message_node = node_data.get("message")
            if message_node:
                author = message_node.get("author", {}).get("role", "unknown")
                content_parts = message_node.get("content", {}).get("parts", [])
                
                # Extract text if parts contain strings
                text_content = "".join([p for p in content_parts if isinstance(p, str)])
                
                if text_content.strip() and author in ["user", "assistant"]:
                    messages.append({"role": author, "content": text_content})

        if messages:
            parsed_sessions.append({
                "id": conv_id,
                "title": title,
                "message_count": len(messages),
                "messages": messages
            })

    print(f"✅ Successfully parsed {len(parsed_sessions)} conversations from ChatGPT export!")
    return parsed_sessions

if __name__ == "__main__":
    # Point this to your extracted conversations.json file
    export_file = "conversations.json"
    sessions = parse_chatgpt_conversations(export_file)
    
    if sessions:
        print(f"\n--- Sample Preview ---")
        print(f"First Conversation Title: '{sessions[0]['title']}'")
        print(f"Total Messages in this thread: {sessions[0]['message_count']}")
        print(f"Last user message preview: {sessions[0]['messages'][-1]['content'][:100]}...")
