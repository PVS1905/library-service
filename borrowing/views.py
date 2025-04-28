from django.utils.timezone import now
from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serialisers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingView(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book")
    http_method_names = ["get", "post"]
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingListSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        book.inventory -= 1
        book.save()
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = self.queryset

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            user_id = self.request.query_params.get("user_id")
            if user_id is not None:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    @action(detail=True,
            methods=["post"],
            url_path="return_book",
            name="return-book"
            )
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        borrowing.actual_return_date = now()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()

        return Response(BorrowingDetailSerializer(borrowing).data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                type=int,
                description="(Admins only) Filter borrowings by "
                            "user ID (example: ?user_id=5)",
            ),
            OpenApiParameter(
                "is_active",
                type=bool,
                description="(Admins only) Filter borrowings by "
                            "active status (example: ?is_active=true)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Create a new borrowing for an authenticated user.",
        request=BorrowingCreateSerializer,
        responses=BorrowingCreateSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
