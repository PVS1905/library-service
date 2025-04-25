from django.utils.timezone import now
from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from borrowing.models import Borrowing
from borrowing.serialisers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)
from user.authentication import CustomHeaderJWTAuthentication


class BorrowingView(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book")
    http_method_names = ["get", "post"]
    authentication_classes = (CustomHeaderJWTAuthentication,)
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
        return Borrowing.objects.filter(user=self.request.user)