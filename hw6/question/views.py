from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import paginator
from django.db.models import Q
from django.http.response import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, View
from django.views.generic.edit import FormMixin

from .forms import QuestionForm, AnswerForm
from .models import Question, Answer
from .utils import send_email_notification


VOTE_OBJECTS = {
    'question': Question,
    'answer': Answer,
}
"""Vote objects mapping"""


class QuestionListView(ListView):
    """Question list endpoint"""
    template_name = 'question/list.html'
    paginate_by = settings.QUESTION_PER_PAGE
    mode = 'list'
    search_query = ''
    tag_query = ''

    def get_queryset(self):
        queryset = Question.objects.load_rating()
        # Filter
        if self.search_query:
            queryset = queryset.filter(
                Q(title__icontains=self.search_query) | Q(text__icontains=self.search_query)
            )
        elif self.tag_query:
            queryset = queryset.filter(tags__name=self.tag_query)
        # Order by
        if self.mode == 'hot':
            queryset = queryset.order_by('-rating')
        elif self.mode in ('search', 'tag'):
            queryset = queryset.order_by('-rating', '-created')
        else:
            queryset = queryset.order_by('-created')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mode'] = self.mode
        context['search_query'] = self.search_query
        context['tag_query'] = self.tag_query
        return context

    def dispatch(self, request, *args, **kwargs):
        if self.mode == 'search':
            self.search_query = self.request.GET.get('q', '')
            if self.search_query.startswith('tag:'):
                return redirect('tag_detail', name=self.search_query[4:])
        elif self.mode == 'tag':
            self.tag_query = kwargs.get('name', '')
        return super().dispatch(request, *args, **kwargs)


class QuestionDetailView(FormMixin, DetailView):
    """Question detail endpoint"""
    model = Question
    form_class = AnswerForm
    template_name = 'question/detail.html'
    paginate_by = settings.ANSWER_PER_PAGE

    def get_queryset(self):
        return Question.objects.load_rating()

    def get_success_url(self):
        return reverse_lazy('question_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page_obj = self.get_answer_page_obj()
        context['page_obj'] = page_obj
        context['answers'] = page_obj.object_list
        context['form'] = self.get_form()
        return context

    def get_answer_page_obj(self):
        answers_paginator = paginator.Paginator(self.object.get_answers(), self.paginate_by)
        try:
            page_obj = answers_paginator.page(self.request.GET.get('page', 1))
        except paginator.InvalidPage:
            page_obj = answers_paginator.page(1)
        return page_obj


    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid():
            answer = self.object.answers.create(text=form.cleaned_data['text'],
                                                question=self.object,
                                                user=request.user)
            send_email_notification(request, self.object, answer)
            return redirect(request.path)
        return self.form_invalid(form)


class QuestionAddView(LoginRequiredMixin, CreateView):
    """Add question endpoint"""
    form_class = QuestionForm
    template_name = 'question/add.html'

    def get_success_url(self):
        return reverse_lazy('question_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AnswerAcceptView(LoginRequiredMixin, View):
    """Accept answer endpoint"""
    def post(self, request, *args, **kwargs):
        answer = get_object_or_404(Answer, pk=kwargs.get('pk'))
        question = answer.question

        if request.user != question.user:
            return HttpResponseForbidden()
        question.accepted_answer = answer
        question.save(update_fields=['accepted_answer'])
        return JsonResponse({})


class VoteView(LoginRequiredMixin, View):
    """Vote endpoint"""
    def post(self, request, *args, **kwargs):
        vote_id = request.POST.get('id')
        vote_value = request.POST.get('value') == 'up'
        vote_object = VOTE_OBJECTS.get(request.POST.get('object'))
        if not vote_object:
            return HttpResponseBadRequest('Invalid object type')

        obj = get_object_or_404(vote_object, pk=vote_id)
        if request.user == obj.user:
            return HttpResponseForbidden()

        vote, created = obj.votes.get_or_create(user=request.user, defaults={'value': vote_value})
        if not created:
            if vote.value == vote_value:
                vote.delete()
            else:
                vote.value = vote_value
                vote.save(update_fields=['value'])

        return JsonResponse({})
