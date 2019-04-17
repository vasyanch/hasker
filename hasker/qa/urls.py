from django.urls import path

from . import views

app_name = 'qa'
urlpatterns = [
    path('pop/', views.IndexView.as_view(flag='pop'), name='index_pop'),
    path('ask/', views.QuestionAddView.as_view(), name='ask'),
    path('question/<int:id>/', views.QuestionDetailsView.as_view(), name='question'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/<str:tag>/', views.SearchTagView.as_view(), name='search_tag'),
    path('vote/', views.VoteView.as_view(), name='vote'),

]
