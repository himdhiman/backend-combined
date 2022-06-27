from notifications.models import *
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

@receiver(post_save, sender=Notification)
def after_creating_notification(sender, instance, created, **kwargs):
    if not created:
        return
    new_obj = NotificationList.objects.create(
        message = "Welcome To DirtyBits !!",
        message_type = "N"
    )
    instance.notifications.add(new_obj)
    instance.save()
    return