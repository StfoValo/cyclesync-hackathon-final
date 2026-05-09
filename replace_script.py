import os
import re
import json

files = [
    "website/static/index.html",
    "website/static/dashboard.html",
    "website/static/user_app.html",
    "website/static/partials/adjuster_tab.html",
    "website/static/js/i18n.js",
    "website/static/js/landing.js",
    "website/static/js/main.js",
    "website/main.py",
    "website/warm_cache.py",
    "website/precompute_cache.py",
    "README.md",
    "ARCHITECTURE.md"
]

changes_summary = {}
total_changes = 0

for fpath in files:
    if not os.path.exists(fpath):
        print(f"File not found: {fpath}")
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    count = 0
    
    def repl_html(match):
        return f"Veri{match.group(1)}Twin{match.group(2)}"
    
    content, n = re.subn(r'Cycle\s*(<span[^>]*>)\s*Sync\s*(</span>)', repl_html, content)
    count += n
    
    n = content.count("CycleSync")
    content = content.replace("CycleSync", "VeriTwin")
    count += n
    
    n = content.count("cyclesync")
    content = content.replace("cyclesync", "veritwin")
    count += n
    
    n = content.count("CycleVision")
    content = content.replace("CycleVision", "VeriVision")
    count += n
    
    if count > 0:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    if count > 0:
        changes_summary[fpath] = count
        total_changes += count

print(json.dumps(changes_summary, indent=2))
print(f"Total changes: {total_changes}")
