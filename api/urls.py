from django.urls import path, include
from rest_framework import routers
from .views import TodoViewSet, RegisterView, ProfileView


#router = routers.DefaultRouter()
#router.register(r'todos', TodoViewSet)

urlpatterns = [
   # path('', include(router.urls)),
    path('register/', RegisterView.as_view()),
    path('profile/', ProfileView.as_view()),
]
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]