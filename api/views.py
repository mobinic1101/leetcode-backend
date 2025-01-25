from rest_framework.views import APIView
from rest_framework.decorators import (
    api_view,
    permission_classes,
    # authentication_classes,
)
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.http import HttpRequest
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import Dict
import requests
import uuid

from . import serializers
from . import models
from .paginations import TopicPagination, ProblemListViewPagination
from . import utils


def DOES_NOT_EXIST(data={"detail": "does not exist."}, status=status.HTTP_404_NOT_FOUND):
    return Response(data=data, status=status)


def BAD_REQUEST(data: dict, status=status.HTTP_400_BAD_REQUEST):
    return Response(data=data, status=status)


def OK(data={}, status=status.HTTP_200_OK):
    return Response(data=data, status=status)


def get_or_404(model: models.models.Model, **kwargs):
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:
        return DOES_NOT_EXIST()
    return obj


# User Views
class UserDetailView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.UserSerializer
    sensitive_fields = ["email", "last_login", "groups"]

    def get(self, request, pk): # todo: add rank to this view
        obj = self.get_object(pk)
        # print(obj)

        if isinstance(obj, Response):
            return obj

        serializer = self.serializer_class(obj)

        data = serializer.data
        if not request.user.is_authenticated:
            data = self.filter_sensitive(data)

        return Response(data=data, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            user = models.CustomUser.objects.get(id=pk)
        except models.CustomUser.DoesNotExist:
            return Response(
                data={"detail": f"user[{pk}] DoesNotExist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return user

    def filter_sensitive(self, data: dict):
        for key in self.sensitive_fields:
            data.pop(key, None)
        return data


@api_view(["POST", "GET"])
@permission_classes([IsAuthenticated])
def my_detail(request: HttpRequest):
    quick_user_fields = ["username", "profile_pic", "solved_count"]
    obj = request.user
    if request.method == "GET":
        if request.query_params.get("quick"):
            data = serializers.UserSerializer(obj, fields=quick_user_fields).data
        else:
            data = serializers.UserSerializer(obj).data

        data.update({"rank": utils.find_current_rank(request)})
        return Response(data=data, status=status.HTTP_200_OK)

    data = {k: v for k, v in request.data.items()}
    print("request.data: ", data)
    profile_pic: InMemoryUploadedFile = data.get("profile_pic", None)
    if profile_pic:
        print(profile_pic.name)
    serializer = serializers.UserSerializer(instance=obj, data=data)

    # Error checking:
    fields_to_restrict = ["is_staff", "is_superuser", "solved_count", "password"]
    for key in fields_to_restrict:
        if key in data:
            return BAD_REQUEST(
                {
                    "detail": f"cannot modify these properties: {', '.join(fields_to_restrict)}"
                }
            )
    if not serializer.is_valid():
        print("serializer is not valid")
        print(serializer.errors)
        return BAD_REQUEST(data=serializer.errors)

    serializer.save()
    return OK(data=serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def leaderboards(request: HttpRequest):
    top_100 = models.CustomUser.objects.filter(solved_count__lt=100).order_by("-solved_count")
    data = serializers.UserSerializer(top_100, many=True).data
    if request.user.is_authenticated:
        data.update({"rank": utils.find_current_rank(request)})
    return OK(data=data)


class UserSolvedProblemsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = serializers.SolvedSerializer

    def get_queryset(self):
        obj = get_or_404(models.CustomUser, id=self.kwargs.get("pk"))
        if isinstance(obj, Response):
            return obj
        return obj.solved.all()


# Problem Views
class ProblemListView(APIView):
    permission_classes = [AllowAny]
    pagination_class = ProblemListViewPagination()

    def get(self, request: HttpRequest):
        queryset = self.get_queryset()
        problems = self.pagination_class.paginate_queryset(queryset, request)
        problem_serializer = serializers.ListProblemSerializer(problems, many=True)
        data = {"problems": problem_serializer.data}
        if request.query_params.get("with_topics", None):
            topics = models.Topic.objects.all()
            topic_serializer = serializers.TopicSerializer(topics, many=True)
            data.update({"topics": topic_serializer.data})

        return OK(data=data)

    def get_queryset(self):
        topics: list = self.request.GET.getlist("topic", '')
        difficulty = self.request.query_params.get("difficulty", "")
        difficulty = (
            difficulty
            if not difficulty
            else (int(difficulty) if 0 < int(difficulty) < 4 else "")
        )
        search = self.request.query_params.get("search", "")
        print(
            f"query_string->\ntopic: {topics}\ndifficulty: {difficulty}\nsearch: {search}"
        )

        filter_criteria = Q(topic__topic__icontains=topics[0]) if not topics[0] else Q(topic__topic__in=topics)
        if difficulty:
            filter_criteria = filter_criteria & Q(difficulty__icontains=difficulty)
        search_criteria = Q(title__icontains=search) | Q(description__icontains=search)
        problems = models.Problem.objects.filter(filter_criteria).filter(
            search_criteria
        )
        return problems


class ProblemDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.ProblemDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        problem = get_or_404(models.Problem, id=self.kwargs.get("pk"))
        return problem


class ProblemCommentView(generics.ListCreateAPIView):
    # View to handle comments on a problem (GET and POST)
    serializer_class = serializers.CommentSerializer

    def post(self, request: HttpRequest, pk):
        comment = request.data.get("comment", "").strip()
        problem = get_or_404(models.Problem, id=pk)

        if not comment:
            return BAD_REQUEST({"detail": "comment cannot be empty."})

        comment = models.Comment.objects.create(
            comment=comment, problem=problem, user=request.user
        )
        return OK()

    def get_queryset(self):
        return models.Comment.objects.filter(Q(problem__id=self.kwargs.get("pk")))

    def get_permissions(self):
        return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]


# Topic Views
class TopicListView(generics.ListAPIView):
    # View to list all topics
    permission_classes = [AllowAny]
    serializer_class = serializers.TopicSerializer
    queryset = models.Topic.objects.all()


# Test Case Views
class TestCaseListView(generics.ListAPIView):
    # View to list test cases for a specific problem
    permission_classes = [AllowAny]
    serializer_class = serializers.TestCaseSerializer

    def get_queryset(self):
        problem = get_or_404(model=models.Problem, id=self.kwargs.get("problem_id"))
        test_cases = models.TestCase.objects.filter(problem=problem)
        return test_cases


# Code running views
class CodeRunningView(APIView):
    # View to handle code running for a specific problem
    permission_classes = []
    serializer_class = serializers.TestCaseSerializer
    code_runner_url = settings.CODE_RUNNER_BASE_URL + "/run-code"

    def post(self, request: HttpRequest, problem_id):
        problem = get_or_404(model=models.Problem, id=problem_id)
        queryset = models.TestCase.objects.filter(problem__id=problem_id)
        data = self.serializer_class(queryset, many=True).data
        # how the data will look like? this is important to know because
        #   we are gonna use this data in the code runner container.
        # or later in the container maybe we converted them using json.loads to get the actual dataStructure.

        # updating the testcases list returned by serializer with allowed_imports and convert it to a dict:
        allowed_imports = problem.allowed_imports if problem.allowed_imports else ""
        data = {
            "execution_id": str(uuid.uuid4()),
            "allowed_imports": allowed_imports,
            "test_cases": str(data),
        }

        python_file = request.data.get("python_file", "")
        if not python_file:
            return BAD_REQUEST(
                {
                    "detail": "you didn't uploaded any file, or maybe you named it wrong in request body,\
the name must be exactly like this-> 'python_file'."
                }
            )
        result = self.send_post_request(data=data, files={"python_file": python_file})
        # print(f"code_runner_status: ", result.status_code)
        return Response(data=result.json(), status=result.status_code)

    def send_post_request(self, data: Dict, files: Dict):
        url = self.code_runner_url
        response = requests.post(url, data=data, files=files)
        return response


@api_view(["GET"])
@permission_classes([AllowAny])
def get_code_running_result(request: HttpRequest, problem_id, execution_id):
    url = f"{settings.CODE_RUNNER_BASE_URL}/get-result/{execution_id}"
    response = requests.get(url)
    code_runner_status_code = response.status_code
    code_runner_result = response.json()

    test_cases = models.TestCase.objects.filter(problem__id=problem_id)
    test_cases = serializers.TestCaseSerializer(test_cases, many=True).data
    test_cases = utils.convert_literal(str(test_cases))
    test_result = code_runner_result.get("test_result")
    compared_list, all_passed = (
        utils.check_test_case_pass(test_cases, test_result)
        if code_runner_status_code == 200
        else ([], False)
    )

    if code_runner_status_code == 200 and request.user.is_authenticated and all_passed:
        user = request.user
        problem = get_or_404(model=models.Problem, id=problem_id)
        if problem not in user.solved.all():
            user.add_solved_problem(problem)

    response_data = {
        "execution_result": code_runner_result,
        "testcase_compare_result": compared_list,
        "all_passed": all_passed,
    }
    return Response(data=response_data, status=code_runner_status_code)


# example value returned from /get-result:
# {'execution_id': '123', 'test_result': [{'id': 1, 'output': 3, 'error': None, 'error_message': None}, {'id': 2, 'output': 5, 'error': None, 'error_message': None}]}
