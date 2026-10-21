from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
import stripe
import asyncio

from .cart import Cart
from .models import Order, OrderItem, Book
from .forms import CustomUserCreationForm


class BookListView(ListView):
    """
    Displays a paginated list of books.
    Optimized with select_related to prevent N+1 query problems.
    """
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 3
    queryset = Book.objects.select_related('category').all().order_by('-id')


class BookDetailView(DetailView):
    """Shows detailed information about a specific book."""
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Allows authorized users with permissions to add a new book."""
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')
    permission_required = 'catalog.add_book'


class BookUpdateView(UpdateView):
    """Allows users to update existing book details."""
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')


class BookDeleteView(DeleteView):
    """Allows users to delete a book with confirmation."""
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('catalog:book_list')


from django.views.generic import CreateView


class RegisterView(CreateView):
    """Handles new user registration."""
    form_class = CustomUserCreationForm
    template_name = 'catalog/register.html'
    success_url = reverse_lazy('login')


def order_create(request):
    """
    Handles order creation from cart items and redirects to payment.
    Includes validation for empty carts.
    """
    cart = Cart(request)

    if request.method == 'POST':
        if len(cart.cart) == 0:
            return redirect('catalog:book_list')

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
                fail_silently=True,
            )

            request.session['order_id'] = order.id
            return redirect('catalog:process_payment')

    return render(request, 'orders/create.html', {'cart': cart})


def process_payment(request):
    """
    Initiates a Stripe checkout session for the current order.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    order_id = request.session.get('order_id')

    if not order_id:
        return redirect('catalog:book_list')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('catalog:payment_success'))
        cancel_url = request.build_absolute_uri(reverse('catalog:payment_cancel'))

        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'Тестова книга Python',
                },
                'unit_amount': 1500,
            },
            'quantity': 1,
        }]

        session_data = {
            'mode': 'payment',
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': line_items,
        }
        session = stripe.checkout.Session.create(**session_data)
        return redirect(session.url, code=303)

    return render(request, 'payment/process.html', locals())


def payment_success(request):
    """Renders the payment success page."""
    return render(request, 'payment/success.html')


def payment_cancel(request):
    """Renders the payment cancellation page."""
    return render(request, 'payment/cancel.html')


# 1. Асинхронний список
async def book_list_async(request):
    """Async view to fetch and display list of books."""
    books = await Book.objects.all().alist()
    return render(request, 'catalog/book_list.html', {'books': books})


# 2. Асинхронні деталі
async def book_detail_async(request, book_id):
    """Async view to fetch and display a specific book."""
    book = await Book.objects.aget(id=book_id)
    return render(request, 'catalog/book_detail.html', {'book': book})