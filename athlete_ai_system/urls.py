from django.contrib import admin
from django.urls import path, include
from users.views import main_page

urlpatterns = [
    path('', main_page, name='main_page'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('workouts/', include('workouts.urls')),
    path('meals/', include('meals.urls')),
]
