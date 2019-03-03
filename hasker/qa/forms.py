from django import forms

from .models import Tag, Question, Answer


class AskForm(forms.Form):
    title = forms.CharField(max_length=100)
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField()

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super(AskForm, self).__init__(*args, **kwargs)

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if not tags:
            return []
        tags = tags.split(',')[:3]
        return [str(t) for t in tags]

    def save(self):
        self.cleaned_data['author'] = self._user
        question = Question(title=self.cleaned_data['title'],
                            text=self.cleaned_data['text'],
                            author=self.cleaned_data['author'])
        question.save(tags_str=self.cleaned_data['tags'])
        return question


class AnswerForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    question = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, user, *args, **kwargs):
        self._user = user
        super(AnswerForm, self).__init__(*args, **kwargs)

    def clean_question(self):
        q_id = self.cleaned_data['question']
        return Question.objects.get(id=q_id)

    def save(self):
        self.cleaned_data['author'] = self._user
        answer = Answer(**self.cleaned_data)
        return answer.save()
