import json

notebook_file = "Transfer_Learning_.ipynb"

with open(notebook_file, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Remove 'widgets' metadata entirely (safe for Jupyter)
if "widgets" in nb.get("metadata", {}):
    del nb["metadata"]["widgets"]

# Save fixed notebook
with open(notebook_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"{notebook_file} is now fixed and can be opened in Jupyter.")
