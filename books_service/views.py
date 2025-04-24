from rest_framework import viewsets

from books_service.models import Book
from library_service.serializers import BookListSerializer


class BookListView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
