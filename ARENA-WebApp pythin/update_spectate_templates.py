#!/usr/bin/env python3
"""
Script to update all spectate templates with background styling and sound effects.
"""
import os

templates_dir = r"C:\Users\ibrah\Desktop\ARENA-WebApp pythin\templates"

spectate_updates = {
    "spectate_tic_tac_toe.html": {
        "background_style": """<style>
  .spectate-bg-ttt {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="max-w-4xl mx-auto">',
        "replacement": '<div class="max-w-4xl mx-auto spectate-bg-ttt min-h-screen">',
    },
    "spectate_connect_four.html": {
        "background_style": """<style>
  .spectate-bg-c4 {
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(234, 179, 8, 0.1) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="max-w-4xl mx-auto">',
        "replacement": '<div class="max-w-4xl mx-auto spectate-bg-c4 min-h-screen">',
    },
    "spectate_maze.html": {
        "background_style": """<style>
  .spectate-bg-maze {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="max-w-4xl mx-auto">',
        "replacement": '<div class="max-w-4xl mx-auto spectate-bg-maze min-h-screen">',
    },
}

def update_spectate_template(filename, config):
    """Update a spectate template with background styling."""
    filepath = os.path.join(templates_dir, filename)
    
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filename}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add background style after {% block content %}
    if '{% block content %}' in content:
        insert_pos = content.find('{% block content %}') + len('{% block content %}')
        content = content[:insert_pos] + '\n' + config["background_style"] + content[insert_pos:]
    
    # Update main div
    if config["search_pattern"] in content:
        content = content.replace(config["search_pattern"], config["replacement"])
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {filename}")
    return True

# Update all spectate templates
print("👁️ Updating spectate templates with backgrounds...\n")
for template, config in spectate_updates.items():
    update_spectate_template(template, config)

print("\n✨ All spectate templates updated successfully!")
