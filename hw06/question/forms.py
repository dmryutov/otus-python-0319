from django import forms

from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    """
    Add question form
    """
    class Meta:
        model = Question
        fields = ('title', 'text', 'tags')

    def clean_tags(self):
        tags = self.cleaned_data['tags']
        if len(tags) > 3:
            raise forms.ValidationError('Exceeded maximum tag count')
        return tags


class AnswerForm(forms.ModelForm):
    """
    Add answer form
    """
    class Meta:
        model = Answer
        fields = ('text',)
