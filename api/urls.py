from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import auth


urlpatterns = [
	path("api-token-auth", obtain_auth_token),
	path("sign-up", auth.sign_up, name="sign_up")
]