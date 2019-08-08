from django.contrib import admin

from .models import Answer, Question, Tag, Vote


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Answer model admin view
    """
    list_display = ('id', 'question', 'user', 'created')
    search_fields = ('question', 'user')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Question model admin view
    """
    list_display = ('id', 'title', 'user', 'created')
    search_fields = ('title', 'user')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Tag model admin view
    """
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    """
    Vote model admin view
    """
    list_display = ('id', 'user', 'value')
    search_fields = ('user',)
