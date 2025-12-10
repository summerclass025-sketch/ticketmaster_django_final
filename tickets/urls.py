from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_events, name='search_events'),

    # CRUD for favorites
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/add/', views.add_favorite, name='add_favorite'),
    path('favorites/update/<int:pk>/', views.update_favorite, name='update_favorite'),
    path('favorites/delete/<int:pk>/', views.delete_favorite, name='delete_favorite'),
]
