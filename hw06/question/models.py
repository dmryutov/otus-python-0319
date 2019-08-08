from django.conf import settings
from django.db import models
from django.db.models import Sum, Case, When, SmallIntegerField

from user.models import User


class Tag(models.Model):
    """
    Tag model
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Vote(models.Model):
    """
    Vote model
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    value = models.BooleanField(default=True)


class QAManager(models.Manager):
    """
    Question and answer models manager
    """
    def load_rating(self):
        """
        Add object rating to queryset
        """
        return self.annotate(rating=Sum(Case(
            When(votes__value=False, then=-1),
            When(votes__value=True, then=1),
            default=0,
            output_field=SmallIntegerField()
        )))


class QABase(models.Model):
    """
    Question and answer base model class
    """
    user = models.ForeignKey(User, models.CASCADE, related_name='%(class)ss')

    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

class Question(QABase):
    """
    Question model
    """
    objects = QAManager()

    tags = models.ManyToManyField(Tag, related_name='questions', blank=True)
    votes = models.ManyToManyField(Vote, related_name='questions', blank=True)
    accepted_answer = models.OneToOneField('Answer', models.CASCADE, blank=True, null=True,
                                           related_name='accept_for_question')

    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def get_answers(self):
        """
        Get question answers

        Returns:
            django.db.models.QuerySet: Answers
        """
        return self.answers.load_rating().order_by('accept_for_question', '-rating', '-created')

    def get_tag_names(self):
        """
        Get question tags

        Returns:
            list: Tag names
        """
        return [tag.name for tag in self.tags.all()]


class Answer(QABase):
    """
    Answer model
    """
    objects = QAManager()

    question = models.ForeignKey(Question, models.CASCADE, related_name='answers')
    votes = models.ManyToManyField(Vote, related_name='answers', blank=True)
