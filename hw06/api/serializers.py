from rest_framework import serializers

from question.models import Answer, Question, Vote


class VoteSerializer(serializers.ModelSerializer):
    """
    Vote instance serializer
    """
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Vote
        fields = ('user', 'value')


class QuestionSerializer(serializers.ModelSerializer):
    """
    Question instance serializer
    """
    user = serializers.StringRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    votes = VoteSerializer(many=True)

    class Meta:
        model = Question
        exclude = ('accepted_answer',)


class AnswerSerializer(serializers.ModelSerializer):
    """
    Answer instance serializer
    """
    user = serializers.StringRelatedField(read_only=True)
    votes = VoteSerializer(many=True)

    class Meta:
        model = Answer
        exclude = ('question',)
