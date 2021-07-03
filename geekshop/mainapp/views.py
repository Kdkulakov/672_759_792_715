from django.shortcuts import render, get_object_or_404

from basketapp.models import Basket
from mainapp.models import ProductCategory, Product


def products(request, pk=None):
    title = 'продукты/каталог'
    basket = []
    if request.user.is_authenticated:
        basket = Basket.objects.filter(user=request.user)

    links_menu = ProductCategory.objects.all()
    products = Product.objects.all().order_by('price')

    if pk is not None:
        if pk == 0:
            products = Product.objects.all().order_by('price')
            category = {'name': 'все'}
        else:
            category = get_object_or_404(ProductCategory, pk=pk)
            products = Product.objects.filter(category__pk=pk).order_by('price')

        context = {
            'title': title,
            'links_menu': links_menu,
            'products': products,
            'category': category,
        }
        return render(request=request, template_name='mainapp/products.html', context=context)

    same_products = Product.objects.all()[3:5]

    context = {
        'title': title,
        'links_menu': links_menu,
        'same_products': same_products,
        'products': products,
        'basket': basket,
    }
    return render(request=request, template_name='mainapp/products.html', context=context)