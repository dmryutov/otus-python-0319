from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView

from question.models import Question
from .paginations import AnswerPagination, QuestionPagination
from .serializers import AnswerSerializer, QuestionSerializer


class QuestionListView(ListAPIView):
    """
    Question list API endpoint

    list:
        Return list of all questions
    """
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination
    permission_classes = ()

    def get_queryset(self):
        return Question.objects.order_by('-created')


class TrendingListView(ListAPIView):
    """
    Popular questions (sorted by rating and date) list API endpoint

    list:
        Return list of top 20 questions
    """
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination
    permission_classes = ()

    def get_queryset(self):
        return Question.objects \
           .load_rating() \
           .order_by('-rating', '-created')[:settings.TRENDING_PER_PAGE]


class SearchListView(ListAPIView):
    """
    Search question list API endpoint

    list:
        Return list of all questions that matches search query
    """
    serializer_class = QuestionSerializer
    pagination_class = QuestionPagination
    permission_classes = ()

    def get_queryset(self):
        queryset = Question.objects.all()
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(text__icontains=search_query)
            )
        return queryset.order_by('-created')


class QuestionDetailView(RetrieveAPIView):
    """
    Question detail API endpoint

    retrieve:
        Return selected question
    """
    serializer_class = QuestionSerializer
    permission_classes = ()
    queryset = Question.objects.all()


class AnswerListView(ListAPIView):
    """
    Answer list API endpoint

    list:
        Return list of all question answers
    """
    serializer_class = AnswerSerializer
    pagination_class = AnswerPagination
    permission_classes = ()

    def get_queryset(self):
        question = get_object_or_404(Question, pk=self.kwargs.get('pk'))
        return question.answers.load_rating() \
            .order_by('-accept_for_question', '-rating', '-created')
