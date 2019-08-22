from qa.models import Question, Answer
from users.models import User
from rest_framework import serializers


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    tags = serializers.SlugRelatedField(slug_field='text', many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('url', 'title', 'author', 'text', 'rating', 'correct_answer', 'tags')


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Answer
        fields = ('url', 'text', 'rating', 'question_id')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')
