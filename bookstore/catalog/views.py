from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import stripe

from .cart import Cart
from .models import Order, OrderItem, Book

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book

class BookListView(ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 3

class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'

class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')
    permission_required = 'catalog.add_book'

class BookUpdateView(UpdateView):
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('catalog:book_list')

from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'catalog/register.html'
    success_url = reverse_lazy('login')


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')

        with transaction.atomic():
            order = Order.objects.create(first_name=first_name, email=email)
            for item in cart.cart.values():
                book = Book.objects.get(id=item['book_id'])
                OrderItem.objects.create(
                    order=order,
                    book=book,
                    price=item['price'],
                    quantity=item['quantity']
                )

            cart.clear()

            send_mail(
                'Order placed',
                f'Hello, {order.first_name}! Your order №{order.id} successfully created.',
                'noreply@bookstore.com',
                [order.email],
                fail_silently=False,
            )

            request.session['order_id'] = order.id
            return redirect('catalog:process_payment')

    return render(request, 'orders/create.html', {'cart': cart})


def process_payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('catalog:payment_success'))
        cancel_url = request.build_absolute_uri(reverse('catalog:payment_cancel'))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Тестова книга Python',
                },
                'unit_amount': 1500,  # Це 15.00 USD (Stripe завжди рахує в центах)
            },
            'quantity': 1,
        }]

        session_data = {
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': line_items,
            'managed_payments': {
                'enabled': False,
            },
        }
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    return render(request, 'payment/process.html', locals())
def payment_success(request):
    return render(request, 'payment/success.html')

def payment_cancel(request):
    return render(request, 'payment/cancel.html')