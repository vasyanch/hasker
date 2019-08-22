from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LogInView.as_view(), name='login'),
    path('profile/<int:id_user>/', views.ProfileView.as_view(), name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:id_user>/edit_data/', views.EditProfileView.as_view(), name='edit_profile'),
]