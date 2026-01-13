#!/usr/bin/env python3
"""
Script to update all game templates with background styling and sound effects.
"""
import os

templates_dir = r"C:\Users\ibrah\Desktop\ARENA-WebApp pythin\templates"

# Dictionary of template updates
updates = {
    "connect four.html": {
        "background_style": """<style>
  .game-bg-connect-four {
    background: linear-gradient(135deg, rgba(220, 38, 38, 0.1) 0%, rgba(234, 179, 8, 0.1) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="max-w-4xl mx-auto">',
        "replacement": '<div class="max-w-4xl mx-auto game-bg-connect-four min-h-screen">',
        "sound_updates": [
            ('class="w-full bg-blue-600 p-2 rounded hover:bg-blue-700 transition font-bold text-sm">↓', 
             'class="w-full bg-blue-600 p-2 rounded hover:bg-blue-700 transition font-bold text-sm" onclick="playSound(\'click\')">↓'),
            ('<p class="text-2xl font-bold text-green-400 mb-4">🎉 Player {{ winner }} Wins!</p>',
             '<p class="text-2xl font-bold text-green-400 mb-4" onclick="playSound(\'win\')">🎉 Player {{ winner }} Wins!</p>'),
            ('<button type="submit" class="w-full bg-blue-600 p-3 rounded hover:bg-blue-700 transition font-semibold">🔄 Play Again</button>',
             '<button type="submit" class="w-full bg-blue-600 p-3 rounded hover:bg-blue-700 transition font-semibold" onclick="playSound(\'click\')">🔄 Play Again</button>'),
            ('<a href="/connect-four" class="bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm">2-Player Mode</a>',
             '<a href="/connect-four" class="bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm" onclick="playSound(\'click\')">2-Player Mode</a>'),
            ('<a href="/connect-four?vs_computer=true" class="bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm">vs AI Mode</a>',
             '<a href="/connect-four?vs_computer=true" class="bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm" onclick="playSound(\'click\')">vs AI Mode</a>'),
            ('<a href="/dashboard" class="mt-6 block bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm">Back to Dashboard</a>',
             '<a href="/dashboard" class="mt-6 block bg-gray-700 p-2 rounded text-center hover:bg-gray-600 transition text-sm" onclick="playSound(\'click\')">Back to Dashboard</a>'),
        ]
    },
    "maze.html": {
        "background_style": """<style>
  .game-bg-maze {
    background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="max-w-4xl mx-auto">',
        "replacement": '<div class="max-w-4xl mx-auto game-bg-maze min-h-screen">',
        "sound_updates": [
            ('type="submit" class="bg-blue-600 p-3 rounded hover:bg-blue-700 transition">',
             'type="submit" class="bg-blue-600 p-3 rounded hover:bg-blue-700 transition" onclick="playSound(\'click\')">'),
            ('<p class="text-2xl font-bold text-green-400 mb-4">🎉 Maze Complete!</p>',
             '<p class="text-2xl font-bold text-green-400 mb-4" onclick="playSound(\'win\')">🎉 Maze Complete!</p>'),
        ]
    },
    "admin.html": {
        "background_style": """<style>
  .admin-bg {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
    background-attachment: fixed;
  }
</style>
""",
        "search_pattern": '<div class="min-h-screen p-6">',
        "replacement": '<div class="min-h-screen p-6 admin-bg">',
        "sound_updates": [
            ('class="w-full bg-blue-600 p-3 rounded hover:bg-blue-700 transition font-bold">',
             'class="w-full bg-blue-600 p-3 rounded hover:bg-blue-700 transition font-bold" onclick="playSound(\'click\')">'),
            ('class="bg-red-600 p-3 rounded hover:bg-red-700 transition text-center">',
             'class="bg-red-600 p-3 rounded hover:bg-red-700 transition text-center" onclick="playSound(\'click\')">'),
        ]
    }
}

def update_template(filename, config):
    """Update a single template file with background styling and sound effects."""
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
    
    # Add sound effects to buttons and links
    for search, replacement in config["sound_updates"]:
        if search in content:
            content = content.replace(search, replacement)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {filename}")
    return True

# Update all templates
print("🎨 Updating game templates with backgrounds and sound effects...\n")
for template, config in updates.items():
    update_template(template, config)

print("\n✨ All templates updated successfully!")
