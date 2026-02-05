from django.urls import path
from .views import log_nutrition, nutrition_history, search_foods

urlpatterns = [
    path('log/', log_nutrition, name='log_nutrition'),
    path('search/', search_foods, name='search_foods'),

    path('history/', nutrition_history, name='nutrition_history'),
]
