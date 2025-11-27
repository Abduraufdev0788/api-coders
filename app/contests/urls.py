from django.urls import path
from .views import Contests

urlpatterns = [
    path("contests/", Contests.as_view(), name="contests" )
]
