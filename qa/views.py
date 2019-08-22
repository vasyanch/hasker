from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import View, generic

from .forms import AskForm, AnswerForm
from .models import Tag, Question, Answer


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

    def get_context_data(self, *args, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['flag'] = self.flag
        context['trending'] = Question.objects.popular()
        context['user'] = self.request.user
        page = self.request.GET.get('page')
        context['page_obj'] = page
        context['objects_list'] = context['paginator'].get_page(page)
        return context


class QuestionAddView(View):
    form_class = AskForm
    template_name = 'qa/question_add.html'

    def __init__(self, *args, **kwargs):
        super(QuestionAddView, self).__init__(*args, **kwargs)
        self.context = {'trending': Question.objects.popular()}

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
    template_name = 'qa/question_details.html'

    def __init__(self, *args, **kwargs):
        super(QuestionDetailsView, self).__init__(*args, **kwargs)
        self.context = {
            'trending': Question.objects.popular(),
            'vote_error': ''
        }

    def get(self, request, *args, **kwargs):
        self.context['question'] = get_object_or_404(Question, id=self.kwargs['id'])
        self.context['user'] = request.user
        if self.context['user'].is_authenticated:
            form = self.form_class(request.user)
            self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        question = get_object_or_404(Question, id=self.kwargs['id'])
        self.context['question'] = question
        self.context['user'] = request.user
        if request.POST.get('rating'):
            rating = int(request.POST.get('rating'))
            models = request.POST.get('models')
            object_id = request.POST.get('object_id')
            if models == 'question' and request.user.userprofile.id_voted_question is None:
                models = get_object_or_404(Question, id=object_id)
                models.vote(rating, request.user)
            elif models == 'answer' and request.user.userprofile.id_voted_answer is None:
                models = get_object_or_404(Answer, id=object_id)
                models.vote(rating, request.user)
            else:
                self.context['vote_error'] = 'Sorry, you can vote only one question and one answer! ' \
                                             'But you can change you choice! See you profile page.'
            question = get_object_or_404(Question, id=self.kwargs['id'])
            self.context['question'] = question
        if request.POST.get('correct_answer'):
            correct_answer = get_object_or_404(Answer, id=request.POST['correct_answer'])
            question.correct_answer = correct_answer
            question.save()
        form = self.form_class(request.user, request.POST)
        if form.is_valid():
            form.save()
            url = question.get_url()
            current_site = get_current_site(request)
            send_mail(
                'New answer!',
                "A new answer for your question!\nFollow this link to see it: {0}{1}".format(current_site.name, url),
                'vasyanch@yandex.ru',
                [question.author.email],
                fail_silently=False
            )
            return HttpResponseRedirect(url)
        self.context['form'] = form
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
