from django.urls import path, include
from rest_framework import routers

from borrowing.views import BorrowingView

router = routers.DefaultRouter()
router.register("", BorrowingView, basename="borrowing")
urlpatterns = [path("", include(router.urls)),
               path('borrowings/<int:pk>/return/',
                    BorrowingView.as_view({'post': 'return_book'}),
                    name='return-book'),
               ]


app_name = "borrowing"
