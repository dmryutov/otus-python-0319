from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

from . import views


urlpatterns = [
    path('schema/', include_docs_urls(title='Hasker')),

    path('user/obtain_token/', obtain_jwt_token, name='obtain_jwt_token'),
    path('user/refresh_token/', refresh_jwt_token, name='refresh_jwt_token'),
    path('user/verify_token/', verify_jwt_token, name='verify_jwt_token'),
    path('user/', include('rest_framework.urls', namespace='rest_framework')),

    path('question/', views.QuestionListView.as_view(), name='api_question_list'),
    path('question/trending/', views.TrendingListView.as_view(), name='api_trending_list'),
    path('question/search/', views.SearchListView.as_view(), name='api_search_list'),
    path('question/<int:pk>/', views.QuestionDetailView.as_view(), name='api_question_detail'),
    path('question/<int:pk>/answer/', views.AnswerListView.as_view(), name='api_answer_list'),
]
