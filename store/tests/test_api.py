from django.contrib.auth.models import User
from django.db.models import Case, Count, When, Avg
from django.urls import reverse
from django.db import connection
from django.test.utils import CaptureQueriesContext 
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase
from rest_framework.utils import json
from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book', owner=self.user,
                                            price='200.00',
                                                author_name='author 1')
        self.book_2 = Book.objects.create(name='Test book 2',   
                                            price='100.00',
                                                author_name='author 5')
        self.book_3 = Book.objects.create(name='Test book author 1', 
                                            price='100.00', 
                                                author_name='author 2')
        UserBookRelation.objects.create(user=self.user, book=self.book_1, 
                                            like=True, rate=5)


    def test_get(self):
        url = reverse('book-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)


    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price':100})
        books = Book.objects.filter(id__in=[self.book_2.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id')  
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


    def test_get_search(self):
        url = reverse('book-list')
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1)))
        ).order_by('id') 
        response = self.client.get(url, data={'search':'author 1'})
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name' : 'Programming in Python 4',
            'price' : 300,
            'author_name' : 'Mark Lutsch'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)


    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name' : self.book_1.name,
            'price' : 300,
            'author_name' : self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()  # Book.objects.get(id=self.book_1.id)
        self.assertEqual(300, self.book_1.price)


    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name' : self.book_1.name,
            'price' : 300,
            'author_name' : self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(
                        string='У вас нема дозволу робити цю дію.', 
                                code='permission_denied')}, response.data)
        self.book_1.refresh_from_db() 
        self.assertEqual(200, self.book_1.price)


    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2', 
                                            is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
            'name' : self.book_1.name,
            'price' : 300,
            'author_name' : self.book_1.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db() 
        self.assertEqual(300, self.book_1.price)



class BookRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book', owner=self.user,
                                            price='200.00',
                                                author_name='author 1')
        self.book_2 = Book.objects.create(name='Test book 2',   
                                            price='100.00',
                                                author_name='author 5')

    def test_like(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'like' : True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, 
                                                    book=self.book_1)
        self.assertTrue(relation.like)
        
        data = {
            'in_bookmarks' : True,
        }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, 
                                                    book=self.book_1)
        self.assertTrue(relation.in_bookmarks)


    def test_rate(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate' : 4,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user, 
                                                    book=self.book_1)
        self.assertEqual(4, relation.rate)


    def test_rate_wrong(self):
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        data = {
            'rate' : 13,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, 
                                    content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
