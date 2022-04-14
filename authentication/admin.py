from django.contrib import admin
from authentication import models


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_verified", "last_login", "auth_provider")


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.AccountVerification)
admin.site.register(models.PasswordChange)
admin.site.register(models.UserProfile)
admin.site.register(models.StaticData)
admin.site.register(models.Avatar)
