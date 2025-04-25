from rest_framework import viewsets

from borrowing.models import Borrowing
from borrowing.serialisers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
)


class BorrowingView(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book")
    http_method_names = ["get", "post"]


    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "retrieve":
                return BorrowingDetailSerializer
        return BorrowingListSerializer



