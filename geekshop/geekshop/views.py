from django.shortcuts import render


def index(request):
    title = 'магазин'
    context = {
        'title': title
    }
    return render(request, 'geekshop/index.html', context=context)


def contacts(request):
    return render(request, 'geekshop/contact.html')