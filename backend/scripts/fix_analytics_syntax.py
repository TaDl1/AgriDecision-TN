
import os

file_path = r"d:\AgriDecision-TN\backend\services\analytics_service.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target string from the error/file view
old_str = "case([(Outcome.outcome == 'success', 1)], else_=0)"
new_str = "case((Outcome.outcome == 'success', 1), else_=0)"

if old_str not in content:
    print("Error: Target string not found!")
    # Debug: print similar lines
    for line in content.splitlines():
        if "case(" in line and "Outcome" in line:
            print(f"Found nearby: {line.strip()}")
else:
    new_content = content.replace(old_str, new_str)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Successfully replaced {content.count(old_str)} occurrences.")
