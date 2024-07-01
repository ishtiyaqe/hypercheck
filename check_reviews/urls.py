from django.urls import path
from .views import *

urlpatterns = [
    path("search/", search, name="search"),
    path("products/<int:id>/", product, name="product"),
    path('api/user/', UserView.as_view(), name='user'),
    path('api/auth/logout/', UserLogout.as_view(), name='user-logout'),
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/myaccount/', MyAccountView.as_view(), name='my-account'),
    path('api/signup/' , UserRegister.as_view() , name="signup"),
    path('api/login/' , UserLogin.as_view() , name="login"),
    
]

