from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class QuestionPagination(PageNumberPagination):
    """
    Question views pagination
    """
    page_size = settings.QUESTION_PER_PAGE


class AnswerPagination(PageNumberPagination):
    """
    Answer views pagination
    """
    page_size = settings.ANSWER_PER_PAGE
