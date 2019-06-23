from rest_framework import routers
from api_hasker import views as api_views


router = routers.DefaultRouter()
router.register('questions', api_views.QuestionViewSet)
router.register('users', api_views.UserViewSet)
router.register('answers', api_views.AnswerViewSet)

urlpatterns = router.urls