from django import forms
from authapp.models import ShopUser
from authapp.forms import ShopUserEditForm


class ShopUserAdminEditForm(ShopUserEditForm):
    class Meta:
        model = ShopUser
        fields = '__all__'