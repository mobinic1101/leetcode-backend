from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from .models import CustomUser


def exists(model, val: dict):
    return True if model.objects.filter(**val).exists() else False


@api_view(["POST"])
@permission_classes([AllowAny])
def sign_up(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")

    if exists(CustomUser, {"username": username}):
        return Response(
            {"error": "this username is already taken."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # password validation
    try:
        validate_password(password)
    except ValidationError as e:
        return Response(
            {"error": " ".join(e.error_list)}, status=status.HTTP_400_BAD_REQUEST
        )

    user = CustomUser.objects.create_user(username=username, password=password)
    token, created = Token.objects.get_or_create(user=user)
    print(token)
    return Response({"token": token.key}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request: HttpRequest):
    pk = request.user.pk
    Token.objects.get(user_id=pk).delete()
    return Response(status=status.HTTP_200_OK)
