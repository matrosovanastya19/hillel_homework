from celery import shared_task
from django.core.mail import send_mail
from django.core.management import call_command
import csv
import os
from django.conf import settings
from .models import Book

@shared_task
def send_order_email(order_id, first_name, email):
    """Асинхронна відправка email при замовленні"""
    send_mail(
        'Order placed',
        f'Hello, {first_name}! Your order №{order_id} successfully created.',
        'noreply@bookstore.com',
        [email],
        fail_silently=True,
    )
    return f"Email sent to {email}"

@shared_task
def clear_sessions():
    """Очищення прострочених сесій з БД"""
    call_command('clearsessions')
    return "Expired sessions cleared."

@shared_task
def generate_report():
    """Генерація CSV звіту по залишкам книг"""
    filepath = os.path.join(settings.BASE_DIR, 'books_report.csv')
    books = Book.objects.all()
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Title', 'Stock', 'Price'])
        for book in books:
            writer.writerow([book.id, book.title, book.stock, book.price])
    return "Report generated."