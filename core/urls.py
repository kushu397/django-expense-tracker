from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(
            template_name='tracker/login.html'
        ),
        name='login'
    ),

    # Logout
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Expense tracker and registration
    path('', include('tracker.urls')),
]