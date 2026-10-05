from django.shortcuts import render

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

class BookCreateView(CreateView):
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')

class BookUpdateView(UpdateView):
    model = Book
    template_name = 'catalog/book_form.html'
    fields = ['title', 'author', 'price', 'description', 'stock', 'category']
    success_url = reverse_lazy('catalog:book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'catalog/book_confirm_delete.html'
    success_url = reverse_lazy('catalog:book_list')