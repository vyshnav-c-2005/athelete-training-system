from django.urls import path
from .views import log_training, training_history

urlpatterns = [
    path('log/', log_training, name='log_training'),
    path('history/', training_history, name='training_history'),
]
