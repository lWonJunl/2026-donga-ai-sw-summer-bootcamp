from django.contrib import admin

from .models import Conversation, Message, UserPreference

admin.site.register(UserPreference)
admin.site.register(Conversation)
admin.site.register(Message)
