from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
	path("obtain_auth_token", obtain_auth_token, name="obtain_auth_token")
]