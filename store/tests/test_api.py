from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from store.models import Book
from store.serializers import BooksSerializer


class BooksAPITestCase(APITestCase):
    def test_get(self):
        book_1 = Book.objects.create(name='Test book', price='0.00')
        book_2 = Book.objects.create(name='Broken', price='-10.00')
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([book_1, book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
