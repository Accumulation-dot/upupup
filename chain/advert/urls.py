from django.urls import path
from advert import views as av
from advert.views import user_records

urlpatterns = [
    path('list/', av.ContentView.as_view()),
    path('add/', av.advert_add),
    path('mine/', av.advert_mine),
         # av.ContentOwnedView.as_view()),
    path('up/', av.advert_up),
    # av.advert_mine),
    path('list/<int:pk>/', av.ContentDetailView.as_view()),
    path('record/', av.RecordView.as_view()),
    path('record/<int:pk>/', av.RecordDetailView.as_view()),
    path('records/', user_records),
    path('all/', av.ContentView.as_view()),
]