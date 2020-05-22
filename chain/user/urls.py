from django.urls import path

from user import views as uv

# from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('register/', uv.UserCreation.as_view()),
    # path('login/', obtain_jwt_token),
    path('login/', uv.login_request),
    path('identify/', uv.identifier_request),
    path('summary/', uv.user_summary),
    path('team/', uv.user_team),
]
