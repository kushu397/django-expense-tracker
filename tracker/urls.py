from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Expense dashboard
    path('', views.dashboard, name='dashboard'),

    # Expense operations
    path('add/', views.add_expense, name='add_expense'),
    path('edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),

    # User registration
    path('register/', views.register, name='register'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]