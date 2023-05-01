from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='expenses'),
    path('add-expense/', add_expense, name='add_expense'),
]
