from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from books_service.models import Book
from books_service.serializers import BookListSerializer, BookDetailSerializer

BOOK_URL = reverse("book:book-list")


def sample_book(**params):
    defaults = {
        "title": "White Fang",
        "author": "Jack London",
        "cover": "HARD",
        "inventory": 20,
        "daily_free": 10.00,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)

def detail_url(book_id):
    return reverse("book:book-detail", args=[book_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        sample_book()

        res = self.client.get(BOOK_URL)
        book = Book.objects.all()
        serializer = BookListSerializer(book, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_book_detail(self):
        book = sample_book()

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookDetailSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_create_book_forbidden(self):
        payload = {
            "title": "Test Title",
            "author": "Jack London",
            "cover": "HARD",
            "inventory": 20,
            "daily_free": 10.00,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "Test Title",
            "author": "Jack London",
            "cover": "HARD",
            "inventory": 20,
            "daily_free": 10.00,
        }
        res = self.client.post(BOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(book, key))

    def test_put_book_allowed(self):
        payload = {
            "title": "Test Title",
            "author": "Jack London",
            "cover": "HARD",
            "inventory": 20,
            "daily_free": 10.00,
        }

        book = sample_book()
        url = detail_url(book.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_movie_not_allowed(self):
        book = sample_book()
        url = detail_url(book.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)