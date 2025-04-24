from rest_framework import viewsets

from books_service.models import Book
from books_service.permissions import IsAdminOrIfAuthenticatedReadOnly
from library_service.serializers import BookListSerializer


class BookListView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
