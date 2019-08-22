from django.shortcuts import render
from django.views import View

from qa.models import Question


class ServerErrorView(View):
    template_name = '500.html'

    def __init__(self, *args, **kwargs):
        super(ServerErrorView, self).__init__(*args, **kwargs)
        self.context = {
            'trending': Question.objects.popular()
        }

    def get(self, request, *args, **kwargs):
        self.context['request_path'] = request.path
        return render(request, self.template_name, self.context)


class NotFoundView(View):
    template_name = '404.html'

    def __init__(self, *args, **kwargs):
        super(NotFoundView, self).__init__(*args, **kwargs)
        self.context = {
            'trending': Question.objects.popular(),
            'exception': ''
        }

    def get(self, request, *args, **kwargs):
        self.context['exception'] = self.kwargs['exception']
        self.context['request_path'] = request.path
        return render(request, self.template_name, self.context)