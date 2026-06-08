import json

with open("scratch/step_127_full.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Root keys:", list(data.keys()))

# Let's search for console log responses recursively inside the object
def find_key_value(obj, target_key, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            if k == target_key or target_key in str(k).lower():
                print(f"Found key '{k}' at path: {new_path}")
                val_str = str(v)
                print(f"Value Snippet: {val_str[:1000]}")
                print("-" * 50)
            find_key_value(v, target_key, new_path)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            find_key_value(item, target_key, f"{path}[{idx}]")

print("Searching for console in step JSON:")
find_key_value(data, "console")
