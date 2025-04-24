from rest_framework.routers import DefaultRouter
from .views import BookListView

app_name = "book"

router = DefaultRouter()
router.register("", BookListView, basename="book")

urlpatterns = router.urls