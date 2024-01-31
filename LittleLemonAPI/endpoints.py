from django.urls import path

from .views import endpoints

urlpatterns = [
    # All endpoints
    path("", endpoints, name="all-endpoints"),
]