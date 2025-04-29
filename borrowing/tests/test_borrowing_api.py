from datetime import timedelta
from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from django.utils import timezone

from rest_framework.test import APIClient

from books_service.tests.test_book_api import sample_book
from borrowing.models import Borrowing
from borrowing.serialisers import BorrowingListSerializer, BorrowingDetailSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")


def sample_borrowing(user, **params):
    defaults = {
        "borrow_date": now(),
        "expected_return_date": now() + timedelta(days=1),
        "actual_return_date": None,
        "book": sample_book(),
        "user": user,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)

def detail_url(borrowing_id):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


class UnauthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@gmail.com",
            "testuser",
        )
        self.client.force_authenticate(self.user)

    # def test_list_borrowings(self):
    #
    #     sample_borrowing(self.user)
    #     res = self.client.get(BORROWING_URL)
    #     borrowing = Borrowing.objects.all()
    #     serializer = BorrowingListSerializer(borrowing, many=True)
    #
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data, serializer.data)

    def test_filter_borrowings_by_user(self):
        sample_borrowing(user=self.user)

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_borrowings_detail(self):
        borrowings = sample_borrowing(user=self.user)

        url = detail_url(borrowings.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowings)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowings(self):
        payload = {
            "borrow_date": now(),
            "expected_return_date": now() + timedelta(days=1),
            "actual_return_date": "",
            "book": sample_book().id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_update_inventory(self):
        book = sample_book()
        start_inventory = book.inventory
        payload = {
            "borrow_date": now(),
            "expected_return_date": now() + timedelta(days=1),
            "actual_return_date": "",
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        book.refresh_from_db()

        self.assertEqual(book.inventory, start_inventory - 1)

    def test_inventory_equal_zero(self):
        book = sample_book()
        book.inventory = 0
        book.save()

        payload = {
            "borrow_date": now(),
            "expected_return_date": now() + timedelta(days=1),
            "actual_return_date": "",
            "book": book.id,
            "user": self.user.id,
        }
        res = self.client.post(BORROWING_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_inventory(self):
        book = sample_book()
        start_inventory = book.inventory
        book.title = "Test"
        book.save()
        borrowing = sample_borrowing(user=self.user, book=book)

        payload = {
            "borrow_date": now(),
            "expected_return_date": now() + timedelta(days=1),
            "actual_return_date": "",
            "book": book.id,
            "user": self.user.id,
        }

        res = self.client.post(reverse('borrowing:return-book', kwargs={'pk': borrowing.id}), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(book.inventory, start_inventory + 1)

    def test_return_inventory_once(self):
        book = sample_book()
        book.title = "Test"
        book.save()
        borrowing = sample_borrowing(user=self.user, book=book)

        payload = {
            "borrow_date": now(),
            "expected_return_date": now() + timedelta(days=1),
            "actual_return_date": "",
            "book": book.id,
            "user": self.user.id,
        }

        res = self.client.post(reverse('borrowing:return-book', kwargs={'pk': borrowing.id}), payload)
        res = self.client.post(reverse('borrowing:return-book', kwargs={'pk': borrowing.id}), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)



class AdminBorrowingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.user = get_user_model().objects.create_user(
            "user@user.com", "testpass", is_staff=False
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        borrow_date = now()
        expected_return_date = now() + timedelta(days=1)


        payload = {
            "borrow_date": borrow_date,
            "expected_return_date": expected_return_date,
            "actual_return_date": "",
            "book": sample_book().id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        borrowing = Borrowing.objects.get(id=res.data["id"])

        for key in payload.keys():
            payload_value = payload[key]
            borrowing_value = getattr(borrowing, key)

            if key == "actual_return_date":
                if payload_value == "" and borrowing_value is None:
                    continue
                else:
                    self.assertEqual(payload_value, borrowing_value)
            elif key == "book" or key == "user":
                self.assertEqual(payload_value, borrowing_value.id)
            else:
                if isinstance(payload_value, datetime):
                    self.assertEqual(payload_value.date(), borrowing_value.date())
                else:
                    self.assertEqual(payload_value, borrowing_value)

    def test_validate_borrowing_expected_return_date(self):
        borrow_date = now()
        expected_return_date = now() - timedelta(days=1)

        payload = {
            "borrow_date": borrow_date,
            "expected_return_date": expected_return_date,
            "actual_return_date": "",
            "book": sample_book().id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_borrowing_actual_return_date_in_future(self):
        borrow_date = now()
        expected_return_date = now() + timedelta(days=1)
        actual_return_date = now() + timedelta(days=2)

        payload = {
            "borrow_date": borrow_date,
            "expected_return_date": expected_return_date,
            "actual_return_date": actual_return_date,
            "book": sample_book().id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validate_borrowing_actual_return_date_before_borrow(self):
        borrow_date = now()
        expected_return_date = now() + timedelta(days=1)
        actual_return_date = now() - timedelta(days=1)

        payload = {
            "borrow_date": borrow_date,
            "expected_return_date": expected_return_date,
            "actual_return_date": actual_return_date,
            "book": sample_book().id,
            "user": self.user.id,
        }

        res = self.client.post(BORROWING_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_borrowings_by_admin(self):
        borrowing_1 = sample_borrowing(user=self.user)
        borrowing_1.book.title = "Test1"
        borrowing_1.book.save()


        borrowing_2 = sample_borrowing(user=self.admin_user)
        borrowing_2.book.title = "Test3"
        borrowing_2.book.save()

        borrowing_3 = sample_borrowing(user=self.user)
        borrowing_3.book.title = "Test4"
        borrowing_3.actual_return_date = now()
        borrowing_3.book.save()

        res = self.client.get(
            BORROWING_URL, {"user_id": f"{self.user.id}", "is_active": True}
        )

        serializer_borrowing_1 = BorrowingListSerializer(borrowing_1)
        serializer_borrowing_3 = BorrowingListSerializer(borrowing_3)

        self.assertIn(serializer_borrowing_1.data, res.data)


        self.assertNotIn(serializer_borrowing_3.data, res.data)

        self.assertNotIn(BorrowingListSerializer(borrowing_2).data, res.data)
