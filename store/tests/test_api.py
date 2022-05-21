from rest_framework.test import APITestCase
from django.urls import reverse
from store.models import Book


class BooksAPITestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Test book', price='0.00')
        url = reverse('book-list')
        print(url)
        response = self.client.get(url)
        print(response.data)