import json

transcript_path = r"C:\Users\HARI\.gemini\antigravity-ide\brain\d3dfc4d5-ed74-4738-af2d-109dc7a24958\.system_generated\logs\transcript.jsonl"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        obj = json.loads(line)
        line_str = json.dumps(obj)
        if 'capture_browser_console_logs' in line_str and obj.get('type') != 'PLANNER_RESPONSE':
            print("Step Index:", obj.get('step_index'))
            print("Type:", obj.get('type'))
            if 'output' in obj:
                print("Output:")
                # Pretty print the output
                try:
                    print(json.dumps(obj['output'], indent=2))
                except:
                    print(str(obj['output'])[:2000])
            print("=" * 80)
