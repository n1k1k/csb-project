from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)

# ❌ A05:2021 Security Misconfiguration (Access to admin page without authentication)
admin.site.has_permission = lambda request: True

# ✅ Fix to restrict admin access to active staff users only
"""
admin.site.has_permission = (
    lambda request: True if request.user.is_active and request.user.is_staff else False
)
"""
