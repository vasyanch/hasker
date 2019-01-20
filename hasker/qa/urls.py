from django.urls import path

from . import views

app_name = 'qa'
urlpatterns = [
    path('', views.index, name='index'),
    path('index/<flag>/', views.index, name='index_pop'),
    path('ask/', views.question_add, name='ask'),
    path('question/<int:id_>/', views.question_details, name='question'),
    path('search/', views.search, name='search'),

]
