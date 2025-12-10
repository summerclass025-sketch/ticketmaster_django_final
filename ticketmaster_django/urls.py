from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tickets.urls')),  # ✅ send all paths to tickets/urls.py
]
