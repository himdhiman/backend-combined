from authentication.models import *
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save
import threading, random


@receiver(post_save, sender=CustomUser)
def after_creating_user(sender, instance, created, **kwargs):
    if not created:
        return
    # if instance.auth_provider != "email":
    # threading.Thread(
    #     target=create_user_notifcation,
    #     kwargs={"email": instance.email, "create": True, "username": instance.username},
    # ).start()

    obj = StaticData.objects.all()
    if len(obj) == 0:
        obj = StaticData.objects.create()
    else:
        obj = obj.first()
    setattr(obj, "users_count", obj.users_count + 1)
    obj.save()
    if obj.avatar_count == 0:
        return
    num = random.randint(0, obj.avatar_count - 1)
    avatar_objs = Avatar.objects.all()
    url = avatar_objs[num].image.url
    url = url.split("?")
    setattr(instance, "profile_pic", url[0])
    instance.save()
    return


@receiver(pre_delete, sender=CustomUser)
def before_deleting_user(sender, instance, *args, **kwargs):
    UserProfile.objects.filter(email=instance.email).delete()
    # threading.Thread(
    #     target=create_user_notifcation,
    #     kwargs={
    #         "email": instance.email,
    #         "create": False,
    #         "username": instance.username,
    #     },
    # ).start()
    obj = StaticData.objects.all().first()
    setattr(obj, "users_count", obj.users_count - 1)
    obj.save()
    return


@receiver(post_save, sender=Avatar)
def after_creating_avatar(sender, instance, *args, **kwargs):
    obj = StaticData.objects.all().first()
    setattr(obj, "avatar_count", obj.avatar_count + 1)
    obj.save()
    return


@receiver(pre_delete, sender=Avatar)
def before_deleting_avatar(sender, instance, *args, **kwargs):
    obj = StaticData.objects.all().first()
    setattr(obj, "avatar_count", obj.avatar_count - 1)
    obj.save()
    try:
        instance.image.storage.delete(instance.image.name)
    except:
        setattr(obj, "avatar_count", obj.avatar_count + 1)
        obj.save()
    return
