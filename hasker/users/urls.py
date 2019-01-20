from django.urls import path

from . import views

app_name='users'
urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_, name='login'),
    path('profile/<int:id_user>/', views.profile, name='profile'),
    path('logout/', views.logout_, name='logout'),
]