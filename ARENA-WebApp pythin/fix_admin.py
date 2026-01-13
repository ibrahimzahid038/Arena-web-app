admin_html = '''{% extends "base.html" %}
{% block title %}Admin Panel - Game Arena{% endblock %}
{% block content %}
<div class="flex flex-col items-center w-full">
    {% if current_user.role != "admin" %}
    <div class="bg-red-600 text-white p-6 rounded-xl mb-4 scale-in max-w-md border-2 border-red-400">
        <h1 class="text-3xl font-bold mb-2">Access Denied</h1>
        <p class="text-lg">Only admins can access this panel.</p>
    </div>
    {% else %}
    
    <h1 class="text-5xl font-bold mb-2 scale-in">Admin Panel</h1>
    <p class="text-gray-400 mb-12 fade-in" style="animation-delay: 0.1s;">Manage users, post advertisements, and control</p>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-6xl">
        <div class="bg-gray-800 rounded-xl p-8 scale-in border-2 border-blue-500 hover:border-blue-400">
            <h2 class="text-3xl font-bold text-blue-300 mb-6">Post Advertisement</h2>        
            <form method="POST" class="space-y-5">
                <input type="hidden" name="action" value="create_ad">
                <div class="fade-in" style="animation-delay: 0.1s;">
                    <label class="block text-sm font-semibold text-blue-200 mb-2">Product Name</label>
                    <input type="text" name="product" required class="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                </div>
                <div class="fade-in" style="animation-delay: 0.15s;">
                    <label class="block text-sm font-semibold text-blue-200 mb-2">Amount Paid ($)</label>
                    <input type="number" name="amount" step="0.01" required class="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                </div>
                <div class="fade-in" style="animation-delay: 0.2s;">
                    <label class="block text-sm font-semibold text-blue-200 mb-2">Duration (Days)</label>
                    <input type="number" name="days" value="7" min="1" required class="w-full px-4 py-3 bg-gray-700 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-4 rounded-lg transition duration-200 button-hover fade-in" style="animation-delay: 0.25s;">Post Advertisement</button>       
            </form>
        </div>

        <div class="bg-gray-800 rounded-xl p-8 scale-in border-2 border-yellow-500 hover:border-yellow-400" style="animation-delay: 0.1s;">
            <h2 class="text-3xl font-bold text-yellow-300 mb-6">Active Advertisements</h2>     
            {% if ads %}
            <div class="space-y-4 max-h-96 overflow-y-auto">
                {% for ad in ads %}
                <div class="bg-gray-700 p-4 rounded-lg border-l-4 border-yellow-400 card-hover">
                    <h3 class="font-bold text-yellow-400 text-lg">{{ ad.product }}</h3>
                    <p class="text-sm text-gray-300">Posted by: <span class="text-blue-300">{{ ad.advertiser.username }}</span></p>
                    <p class="text-sm text-gray-400">Amount: ${{ ad.amount_paid }}</p>    
                    <p class="text-sm text-gray-400">Expires: {{ ad.expires_at.strftime('%Y-%m-%d %H:%M') }}</p>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-gray-400 text-center py-8">No advertisements posted yet.</p>
            {% endif %}
        </div>
    </div>

    <div class="mt-12 bg-gray-800 rounded-xl p-8 w-full max-w-6xl scale-in border-2 border-purple-500 hover:border-purple-400" style="animation-delay: 0.2s;">
        <h2 class="text-3xl font-bold text-purple-300 mb-8">User Management</h2>
        {% if users %}
        <div class="overflow-x-auto">
            <table class="w-full text-gray-300">
                <thead class="border-b-2 border-gray-600 bg-gray-700">
                    <tr>
                        <th class="text-left py-3 px-4 font-bold">Username</th>
                        <th class="text-left py-3 px-4 font-bold">Role</th>
                        <th class="text-left py-3 px-4 font-bold">Created</th>
                        <th class="text-left py-3 px-4 font-bold">Actions</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-700">
                    {% for user in users %}
                    <tr class="hover:bg-gray-700 transition">
                        <td class="py-3 px-4 font-semibold">{{ user.username }}</td>
                        <td class="py-3 px-4">
                            <span class="px-3 py-1 rounded-full text-xs font-bold {% if user.role == 'admin' %}bg-red-600 text-white{% elif user.role == 'player' %}bg-blue-600 text-white{% else %}bg-gray-600 text-white{% endif %}">
                                {{ user.role }}
                            </span>
                        </td>
                        <td class="py-3 px-4 text-sm">{{ user.created_at.strftime('%Y-%m-%d') }}</td>
                        <td class="py-3 px-4">
                            {% if user.id != current_user.id %}
                            <div class="flex gap-2 flex-wrap">
                                {% if user.role == 'player' %}
                                <form method="POST" style="display:inline;">
                                    <input type="hidden" name="action" value="grant_admin">
                                    <input type="hidden" name="user_id" value="{{ user.id }}">
                                    <button type="submit" class="bg-green-600 hover:bg-green-700 text-white font-bold py-1 px-3 rounded transition text-xs button-hover">Grant Admin</button>
                                </form>
                                {% else %}
                                <form method="POST" style="display:inline;">
                                    <input type="hidden" name="action" value="revoke_admin">
                                    <input type="hidden" name="user_id" value="{{ user.id }}">
                                    <button type="submit" class="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-1 px-3 rounded transition text-xs button-hover">Revoke Admin</button>
                                </form>
                                {% endif %}
                                <form method="POST" style="display:inline;" onsubmit="return confirm('Delete this user permanently?');">
                                    <input type="hidden" name="action" value="delete_user">
                                    <input type="hidden" name="user_id" value="{{ user.id }}">
                                    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white font-bold py-1 px-3 rounded transition text-xs button-hover">Delete</button>
                                </form>
                            </div>
                            {% else %}
                            <span class="text-blue-400 font-bold">Master Admin</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="text-gray-400 text-center py-8">No users found.</p>
        {% endif %}
    </div>

    {% endif %}
</div>
{% endblock %}
'''

with open("templates/admin.html", "w", encoding="utf-8") as f:
    f.write(admin_html)

print("Admin template updated!")
