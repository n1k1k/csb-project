from django.contrib import admin
from .models import Post, Comment

admin.site.register(Post)
admin.site.register(Comment)

admin.site.has_permission = (
    lambda request: True if request.user.is_active and request.user.is_staff else False
)
