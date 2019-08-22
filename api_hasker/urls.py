from django.urls import path
from rest_framework import routers
from api_hasker import views as api_views
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='Hasker API')

router = routers.DefaultRouter()
router.register('questions', api_views.QuestionViewSet)
router.register('users', api_views.UserViewSet)
router.register('answers', api_views.AnswerViewSet)

urlpatterns = [
    path('swagger_schema', schema_view)
]+ router.urls