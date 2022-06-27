from django.db import models
from django.utils.timezone import now

class NotificationList(models.Model):
    message_type_choices = (("N", "Notify"), ("W", "Warning"))
    message = models.TextField(blank=True, null=True)
    message_type = models.CharField(choices=message_type_choices, max_length=20)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(default=now, editable=True)

    def __str__(self):
        return str(self.id)


class Notification(models.Model):
    user = models.IntegerField(blank=False, unique=True)
    notifications = models.ManyToManyField(NotificationList, blank=True)

    def __str__(self):
        return self.user


