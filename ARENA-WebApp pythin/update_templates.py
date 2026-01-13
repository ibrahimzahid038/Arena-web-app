#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

ads_section = '''
  <!-- Advertisements -->
  {% if ads %}
  <div class="mt-8">
    <h3 class="text-2xl font-bold mb-4 text-center">Featured Advertisements</h3>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {% for ad in ads %}
      <div class="bg-gradient-to-br from-yellow-600 to-yellow-700 p-6 rounded-lg border-2 border-yellow-400 shadow-lg hover:shadow-xl transition">
        <div class="text-yellow-100 text-sm font-semibold mb-2">📢 ADVERTISEMENT</div>
        <h4 class="text-xl font-bold text-white mb-2">{{ ad.product }}</h4>
        <p class="text-yellow-50 text-sm">💰 Featured Product</p>
        <div class="mt-4 pt-4 border-t border-yellow-400">
          <p class="text-xs text-yellow-100">Expires: {{ ad.expires_at.strftime('%Y-%m-%d') }}</p>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endif %}
'''

def update_template(filename):
    template_path = f"templates/{filename}"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if ads section already exists
        if "<!-- Advertisements -->" in content:
            print(f"✓ {filename} already has ads section")
            return
        
        marker = "  <!-- Spectator Links -->"
        
        if marker in content:
            content = content.replace(marker, ads_section + "\n\n" + marker)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filename} updated successfully")
        else:
            print(f"✗ Marker not found in {filename}")
    except Exception as e:
        print(f"✗ Error updating {filename}: {e}")

# Update all game templates
update_template("connect four.html")
update_template("maze.html")

print("\nTemplate update complete!")
