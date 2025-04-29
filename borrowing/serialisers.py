from rest_framework import serializers
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from books_service.serializers import BookListSerializer
from borrowing.models import Borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    title = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="title", source="book"
    )
    author = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="author", source="book"
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "title",
            "author",
            "borrow_date",
            "is_active",
        )


class BorrowingCreateSerializer(BorrowingListSerializer):

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
            "actual_return_date",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs=attrs)
        attrs["borrow_date"] = timezone.now()
        book = attrs["book"]

        if book.inventory < 1:
            raise ValidationError("This book is currently unavailable.")
        Borrowing.validate_borrowing(
            attrs["borrow_date"],
            attrs["expected_return_date"],
            attrs["actual_return_date"],
        )
        return data


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookListSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )
