from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import TaskLog


@receiver(post_save, sender=TaskLog)
def broadcast_new_log(sender, instance, created, **kwargs):
    """
    Broadcast new log entries to WebSocket clients.
    """
    if not created or not instance.session:
        return
    
    channel_layer = get_channel_layer()
    room_group_name = f"session_{instance.session.session_id}"

    # Broadcast to all clients in this session's room
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'new_log',
            'data': instance.to_dict()
        }
    )
