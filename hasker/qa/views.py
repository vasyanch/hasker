from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View, generic

from .forms import AskForm, AnswerForm
from .models import Tag, Question, Answer


class VoteView(View):
    # 'SORRY! You can vote only for one question and one answer'
    def post(self, request, *args, **kwargs):
        models = request.POST.get('models')
        url = request.POST.get('url')
        object_id = request.POST.get('object_id')
        if models == 'question' and request.user.userprofile.id_voted_question is None:
            models = get_object_or_404(Question, id=object_id)
        elif models == 'answer' and request.user.userprofile.id_voted_answer is None:
            models = get_object_or_404(Answer, id=object_id)
        else:
            return HttpResponseRedirect(url)
        rating = int(request.POST.get('rating'))
        models.vote(rating, request.user, object_id)
        return HttpResponseRedirect(url)


class IndexView(generic.ListView):
    model = Question
    template_name = 'qa/index.html'
    context_object_name = 'list_questions'
    paginate_by = 20
    flag = 'new'

    def get_queryset(self):
        if self.flag == 'new':
            return Question.objects.new()
        if self.flag == 'pop':
            return Question.objects.popular()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['flag'] = self.flag
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
        form = self.form_class(request.user)
        self.context['user'] = request.user
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, id=self.kwargs['id'])
        self.context['question'] = question
        self.context['user'] = request.user
        try:
            correct_answer = get_object_or_404(Answer, id=request.POST['correct_answer'])
        except KeyError:
            pass
        else:
            question.correct_answer = correct_answer
            question.save()
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            url = question.get_url()
            send_mail(
                'New answer!',
                """A new answer for your question!\nFollow this link to see it: {}""".format(url),
                'vasyanch@yandex.ru',
                [question.author.email],
                fail_silently=False
            )
            return HttpResponseRedirect(url)
        self.context['form'] = form
        return render(request, self.template_name, self.context)


class NotFoundView(View):
    template_name = '404.html'
    context = {
        'trending': Question.objects.popular(),
        'exception': '',
    }

    def get(self, request, *args, **kwargs):
        self.context['exception'] = self.kwargs['exception']
        self.context['request_path'] = request.path
        return render(request, self.template_name, self.context)


class ServerError(View):
    template_name = '500.html'
    context = {'trending': Question.objects.popular()}

    def get(self, request, *args, **kwargs):
        self.context['request_path'] = request.path
        return render(request, self.template_name, self.context)


class SearchView(IndexView):
    template_name = 'qa/search_result.html'

    def get_queryset(self):
        query = self.request.GET.get('query')
        if not query:
            return Question.objects.none()
        if query.startswith('tag'):
            self.template_name = 'qa/tag_search_result.html'
            tag_text = query.split(':')[1]
            try:
                tag_object = Tag.objects.get(text=tag_text.strip())
                ans = tag_object.questions.all()
            except Tag.DoesNotExist:
                return Question.objects.none()
        else:
            title_list = Question.objects.filter(title__icontains=query)
            text_list = Question.objects.filter(text__icontains=query)
            ans = title_list | text_list
        return ans.order_by('-rating', '-added_at')


class SearchTagView(IndexView):
    template_name = 'qa/tag_search_result.html'

    def get_queryset(self):
        tag_text = self.kwargs['tag']
        tag_object = Tag.objects.get(text=tag_text.strip())
        ans = tag_object.questions.all()
        return ans.order_by('-rating', '-added_at')
