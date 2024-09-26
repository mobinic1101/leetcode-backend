from django.utils.deprecation import MiddlewareMixin
from ..models import Problem
from ..utils import Class


class QueryParameterMiddleware(MiddlewareMixin):
    valid_parameters = Class(Problem).extract_attr_names(
        ignore=["hint", "template", "likes"]
        ).append("search")
    
    def process_request(self, request):
        query_parameters = request.query_params

        

        