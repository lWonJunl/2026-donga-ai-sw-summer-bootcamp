from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .context_cache import (
    invalidate_conversation_context,
    refresh_conversation_context,
)
from .models import Conversation, Message


@receiver(post_save, sender=Message)
def refresh_context_after_message_save(sender, instance, **kwargs):
    if instance.conversation_id:
        refresh_conversation_context(instance.conversation)


@receiver(post_delete, sender=Message)
def update_context_after_message_delete(sender, instance, **kwargs):
    if not instance.conversation_id:
        return
    conversation = Conversation.objects.filter(id=instance.conversation_id).first()
    if conversation is None:
        invalidate_conversation_context(instance.conversation_id)
    else:
        refresh_conversation_context(conversation)


@receiver(post_delete, sender=Conversation)
def invalidate_context_after_conversation_delete(sender, instance, **kwargs):
    invalidate_conversation_context(instance.id)
