from django.shortcuts import render

from basketapp.models import Basket
from mainapp.models import Product


def index(request):
    title = 'магазин'

    products = Product.objects.all()[:3]
    basket = []
    if request.user.is_authenticated:
        basket = Basket.objects.filter(user=request.user)

    context = {
        'title': title,
        'products': products,
        'basket': basket
    }
    return render(request, 'geekshop/index.html', context=context)


def contacts(request):
    return render(request, 'geekshop/contact.html')