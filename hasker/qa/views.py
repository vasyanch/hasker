from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View, generic

from .forms import AskForm, AnswerForm
from .models import Tag, Question, Answer


class IndexView(generic.ListView):
    template_name = 'qa/index.html'
    context_object_name = 'list_questions'
    paginate_by = 10
    flag = 'new'

    def get_queryset(self):
        set_questions = None
        if self.flag == 'new':
            set_questions = Question.objects.new()
        if self.flag == 'pop':
            set_questions = Question.objects.popular()
        return set_questions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trending'] = Question.objects.popular()
        context['user'] = self.request.user
        page = self.request.GET.get('page')
        context['page_obj'] = page
        context['objects_list'] = context['paginator'].get_page(page)
        return context


class QuestionAddView(View):
    form_class = AskForm
    context = {'trending': Question.objects.popular()}
    template_name = 'qa/question_add.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(request.user)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            question = form.save()
            url = question.get_url()
            return HttpResponseRedirect(url)
        self.context['form'] = form
        return render(request, self.template_name, self.context)


class QuestionDetailsView(View):
    form_class = AnswerForm
    context = {'trending': Question.objects.popular()}
    template_name = 'qa/question_details.html'

    def get(self, request, *args, **kwargs):
        self.context['question'] = get_object_or_404(Question, id=self.kwargs['id'])
        form = self.form_class(request, initial={'question': self.context['question'].id})
        self.context['user'] = request.user
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.user, request.POST)
        self.context['question'] = get_object_or_404(Question, id=self.kwargs['id'])
        if form.is_valid():
            form.save()
            url = self.context['question'].get_url()
            return HttpResponseRedirect(url)
        self.context['user'] = request.user
        self.context['form'] = form
        return render(request, self.template_name, self.context)


def not_found(request, exception, template_name='404.html'):
    context = {
        'trending': Question.objects.popular(),
        'request_path': request.path,
        'exception': exception,
    }
    return render(request, template_name, context, status=404)


def server_error(request, template_name='500.html'):
    context = {
        'trending': Question.objects.popular(),
        'request_path': request.path,
    }
    return render(request, template_name, context, status=500)


def search(request):
    pass
