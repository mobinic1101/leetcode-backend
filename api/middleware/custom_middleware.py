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
