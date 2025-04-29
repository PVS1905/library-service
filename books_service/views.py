from drf_spectacular.utils import extend_schema
from rest_framework import viewsets

from books_service.models import Book
from books_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from books_service.serializers import BookListSerializer


class BookListView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @extend_schema(
        description="Create a new book. Available only to administrators.",
        request=BookListSerializer,
        responses=BookListSerializer,
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
