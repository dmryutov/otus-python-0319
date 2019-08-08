from django import template
from django.conf import settings

from question.models import Question


register = template.Library()


@register.simple_tag
def trending_questions():
    """
    Show popular questions (sorted by rating and date)
    """
    return Question.objects \
        .load_rating() \
        .order_by('-rating', '-created')[:settings.TRENDING_PER_PAGE]
