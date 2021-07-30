from django.db import transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, DeleteView, DetailView, UpdateView

from .models import Order, OrderItem
from basketapp.models import Basket
from .forms import OrderForm, OrderItemForm

from django.contrib.auth.mixins import LoginRequiredMixin


class OrderList(LoginRequiredMixin, ListView):
    model = Order

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreate(LoginRequiredMixin, CreateView):
    model = Order
    fields = []
    context_object_name = 'object'
    success_url = reverse_lazy('ordersapp:orders_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFormSet(self.request.POST)
        else:
            basket_items = Basket.objects.filter(user=self.request.user)
            if basket_items.exists():
                OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=basket_items.count())
                formset = OrderFormSet()
                for num, form in enumerate(formset.forms):
                    form.initial['product'] = basket_items[num].product
                    form.initial['quantity'] = basket_items[num].quantity
                    form.initial['price'] = basket_items[num].product.price
                basket_items.delete()
            else:
                formset = OrderFormSet()

        data['orderitems'] = formset

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_total_cost() == 0:
            self.object.delete()

        return super(OrderCreate, self).form_valid(form)


class OrderUpdate(LoginRequiredMixin, UpdateView):
    model = Order
    fields = []
    context_object_name = 'object'
    success_url = reverse_lazy('ordersapp:orders_list')

    def get_context_data(self, **kwargs):
        data = super(OrderUpdate, self).get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            data['orderitems'] = OrderFormSet(self.request.POST, instance=self.object)
        else:
            formset = OrderFormSet(instance=self.object)
            for form in formset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price

            data['orderitems'] = formset

        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_total_cost() == 0:
            self.object.delete()

        return super(OrderUpdate, self).form_valid(form)


class OrderDelete(DeleteView):
   model = Order
   success_url = reverse_lazy('ordersapp:orders_list')


class OrderRead(DetailView):
   model = Order
   template_name = 'ordersapp/order_detail.html'

   def get_context_data(self, **kwargs):
       context = super(OrderRead, self).get_context_data(**kwargs)
       context['title'] = 'заказ/просмотр'
       return context


def order_forming_complete(request, pk):
   order = get_object_or_404(Order, pk=pk)
   order.status = Order.SENT_TO_PROCEED
   order.save()

   return HttpResponseRedirect(reverse('ordersapp:orders_list'))


@receiver(pre_save, sender=OrderItem)
@receiver(pre_save, sender=Basket)
def product_quantity_update_save(sender, update_fields, instance, **kwargs):
    if update_fields == 'quantity' 'product':
        if instance.pk:
            instance.product.quantity -= instance.quantity.sender.get_item(instance.pk).quantity
        else:
            instance.product.quantity -= instance.quantity
        instance.save()


@receiver(pre_save, sender=OrderItem)
@receiver(pre_save, sender=Basket)
def product_quantity_update_delete(sender, instance, **kwargs):
    instance.product.quantity += instance.quantity
    instance.product.save()