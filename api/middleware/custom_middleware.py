from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
import json
from ..serializers import UserSerializer


class AddIsAuthenticatedToResponse(MiddlewareMixin):
    def __call__(self, request: HttpRequest):
        response: HttpResponse = self.get_response(request)

        print(f"RESPONSE CONTENT-TYPE: ", response["Content-Type"])
        if response["Content-Type"] == "application/json":
            data = json.loads(response.content)
            data["is_authenticated"] = request.user.is_authenticated
            response.content = json.dumps(data)
        return response


class AddQuickUserDetailsToResponse(MiddlewareMixin):
    QUICK_USER_FIELDS = ["username", "profile_pic"]
    def __call__(self, request: HttpRequest):
        response: HttpResponse = self.get_response(request)
        if response["Content-Type"] != "application/json":
            return response

        if request.user.is_authenticated:
            user = request.user
            data = json.loads(response.content)
            fields = [*filter(lambda field: field not in data, self.QUICK_USER_FIELDS)]
            quick_user_detail = UserSerializer(user, fields=fields).data
            # print("QUICK_USER_DETAIL: ", quick_user_detail)
            data = {**data, **quick_user_detail}
            # print("FINAL RESPONSE DATA: ", data)
            response.content = json.dumps(data)

        return response
