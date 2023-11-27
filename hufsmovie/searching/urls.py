from django.urls import path
from .views import *
from .minseok import*

app_name = 'searching'

urlpatterns = [
    # path('recommend/<str:movie_title>/', Recommend.as_view()),
    path('', Search.as_view()),
    path('recommend/<str:movie_title>/', Test.as_view()),
]