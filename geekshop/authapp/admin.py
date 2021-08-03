from django.contrib import admin

from authapp.models import ShopUser, ShopUserProfile

admin.site.register(ShopUser)
admin.site.register(ShopUserProfile)
