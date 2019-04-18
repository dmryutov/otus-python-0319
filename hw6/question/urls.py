from django.urls import path

from . import views


urlpatterns = [
    path('', views.QuestionListView.as_view(), name='question_list'),
    path('hot/', views.QuestionListView.as_view(mode='hot'), name='question_hot'),
    path('search/', views.QuestionListView.as_view(mode='search'), name='question_search'),
    path('add/', views.QuestionAddView.as_view(), name='question_add'),
    path('<int:pk>/', views.QuestionDetailView.as_view(), name='question_detail'),

    path('tag/<str:name>/', views.QuestionListView.as_view(mode='tag'), name='tag_detail'),

    path('answer/<int:pk>/accept/', views.AnswerAcceptView.as_view(), name='accept_answer'),
    path('vote/', views.VoteView.as_view(), name='vote'),
]
