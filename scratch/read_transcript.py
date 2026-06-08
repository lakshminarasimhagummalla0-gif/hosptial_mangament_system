import json

transcript_path = r"C:\Users\HARI\.gemini\antigravity-ide\brain\d3dfc4d5-ed74-4738-af2d-109dc7a24958\.system_generated\logs\transcript.jsonl"

try:
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            # Check if this is a tool call or response related to console logs
            line_str = json.dumps(obj)
            if 'console' in line_str.lower() or 'log' in line_str.lower():
                # Print only relevant parts to avoid flooding
                if 'capture_browser_console_logs' in line_str or 'console' in line_str:
                    print("Step Index:", obj.get('step_index'))
                    print("Type:", obj.get('type'))
                    # Let's print keys and some contents
                    content = obj.get('content', '')
                    if content:
                        print("Content Snippet:", content[:500])
                    tool_calls = obj.get('tool_calls', [])
                    if tool_calls:
                        print("Tool Calls:", tool_calls)
                    output = obj.get('output', '')
                    if output:
                        # If output is a string, print a snippet, otherwise format it
                        out_str = str(output)
                        print("Output Snippet:", out_str[:1000])
                    print("-" * 50)
except Exception as e:
    print("Error:", e)
