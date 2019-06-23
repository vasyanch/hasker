from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from qa.models import Question, Answer
from users.models import User
from .serializers import QuestionSerializer, AnswerSerializer, UserSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.new()
    serializer_class = QuestionSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'text')
    ordering_fields = ('added_at', 'rating')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('question_id',)
