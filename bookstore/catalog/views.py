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