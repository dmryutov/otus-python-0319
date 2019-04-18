from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


def send_email_notification(request, question, answer):
    """
    Send email notification to question author after posting new answer

    Args:
        request (django.core.handlers.wsgi.WSGIRequest): HTTP request
        question (question.models.Question): Question instance
        answer (question.models.Answer): Answer instance
    """
    subject = 'New answer for your question'
    to_email = [question.user.email]
    html_message = render_to_string('email/answer.html', {
        'answer': answer,
        'question': question,
        'link': request.build_absolute_uri(reverse('question_detail', kwargs={'pk': question.pk})),
    })
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.EMAIL_FROM, to_email, html_message=html_message)
