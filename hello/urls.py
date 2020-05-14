from django.urls import path
from .views import *


urlpatterns = [
    path('', VisitorListView.as_view()),
]
