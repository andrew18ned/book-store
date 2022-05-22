from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from store.models import Book
from store.serializers import BooksSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(name='Test book', price='200.00',
                                                author_name='author 1')
        self.book_2 = Book.objects.create(name='Test book 2', price='100.00',
                                                author_name='author 5')
        self.book_3 = Book.objects.create(name='Test book author 1', price='1000.00',
                                                author_name='author 2')


    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], 
                                                            many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search':'author 1'})
        serializer_data = BooksSerializer([self.book_1, self.book_3], 
                                                            many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
