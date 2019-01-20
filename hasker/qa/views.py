from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect

from .models import Tag, Question, Answer, paginate
from .forms import AskForm, AnswerForm


def index(request, flag='new'):
    if flag == 'new':
        set_questions = Question.objects.new()
    elif flag == 'pop':
        set_questions = Question.objects.popular()
    else:
        set_questions = None
    trending = Question.objects.popular()
    paginator, page = paginate(request, set_questions)
    paginator.baseurl = '/?page='
    user = request.user
    return render(request, 'qa/index.html', {
        'list_questions': page.object_list,
        'paginator': paginator,
        'page': page,
        'user': user,
        'trending': trending,
    })


def question_add(request):
    if request.method == 'POST':
        form = AskForm(request.user, request.POST)
        if form.is_valid():
            question = form.save()
            url = question.get_url()
            return HttpResponseRedirect(url)
    else:
        form = AskForm(request.user)
    trending = Question.objects.popular()
    return render(request, 'qa/question_add.html', {
        'form': form,
        'trending': trending,
    })


def question_details(request, id_):
    question = get_object_or_404(Question, id=id_)
    user = request.user
    trending = Question.objects.popular()
    if request.method == 'POST':
        form = AnswerForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            url = question.get_url()
            print(url)
            return HttpResponseRedirect(url)
    else:
        form = AnswerForm(request.user, initial={'question': question.id})
    return render(request, 'qa/question_details.html', {
        'question': question,
        'form': form,
        'trending': trending,
        'user': user,
    })


def search(request):
    pass

