from django.utils import timezone
from django.conf import settings

from django.db import models

from books_service.models import Book
from django.core.exceptions import ValidationError


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.ForeignKey(
        Book, related_name="borrowings",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    @property
    def is_active(self):
        return self.actual_return_date is None

    @staticmethod
    def validate_borrowing(
            borrow_date,
            expected_return_date,
            actual_return_date=None
    ):
        if expected_return_date is None:
            raise ValidationError(
                "Both borrow date and expected return date must be provided."
            )

        if borrow_date > expected_return_date:
            raise ValidationError(
                "Expected return date must be after borrow date."
            )

        if actual_return_date:
            if actual_return_date < borrow_date:
                raise ValidationError(
                    "Actual return date cannot be earlier than the rental date"
                )
            if actual_return_date > timezone.now():
                raise ValidationError(
                    "Actual return date cannot be in the future"
                )

    def clean(self):
        Borrowing.validate_borrowing(
            self.borrow_date,
            self.expected_return_date,
            self.actual_return_date,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Book: {self.book.title}, Borrowed on: {self.borrow_date}"

    class Meta:
        ordering = ["actual_return_date", "-borrow_date"]
