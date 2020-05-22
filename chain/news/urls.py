from django.urls import path

from news import views

# NewsListView, NewsRecordView, NewsRecordInsertView, news_list

urlpatterns = [
    # path('list/', views.news_list),
    # path('list/', views.ContentView.as_view()),
    # path('record/', views.RecordView.as_view()),
    # path('record/<int:pk>/', views.RecordDetailView.as_view()),
    path('list/', views.NewsView.as_view()),
    path('task/', views.task_request),
    path('check/', views.task_check),
]


