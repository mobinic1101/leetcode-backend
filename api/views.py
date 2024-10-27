from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.http import HttpRequest 
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor

from . import serializers
from . import models
from .paginations import TopicPagination
from . import utils

def DOES_NOT_EXIST(data={"error": "does not exist."}, status=status.HTTP_404_NOT_FOUND):
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

	def get(self, request, pk):
		obj = self.get_object(pk)
		print(obj)

		if isinstance(obj, Response):
			return obj

		serializer = self.serializer_class(obj)

		data = serializer.data
		if not request.user.is_authenticated:
			data = self.filter_sensitive(data)
		
		return Response(data=data, status=status.HTTP_200_OK)

	def put(self, request, pk):
		obj = self.get_object(pk)
		data = request.data
		serializer = self.serializer_class(instance=obj, data=data)

		# Error checking:
		fields_to_restrict = ["is_staff", "is_superuser", "solved_count"]
		for key in fields_to_restrict:
			if key in data:
				return BAD_REQUEST({
					"error":f"cannot modify these properties: {', '.join(fields_to_restrict)}"
					})
		if not serializer.is_valid():
			return BAD_REQUEST(data=serializer.error_messages)
		
		serializer.save()
		return OK(data=serializer.data)

	def get_object(self, pk):
		try:
			user = models.CustomUser.objects.get(id=pk)
		except models.CustomUser.DoesNotExist:
			return Response(data={"error": f"user[{pk}] DoesNotExist"}, status=status.HTTP_404_NOT_FOUND)
		return user

	def get_permissions(self):
		if self.request.method.lower() == 'put':
			return [IsAuthenticated()]
		return [AllowAny()]

	def filter_sensitive(self, data: dict):
		for key in self.sensitive_fields:
			data.pop(key, None)
		return data


class UserSolvedProblemsView(generics.ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = serializers.SolvedSerializer
	pagination_class = PageNumberPagination
	
	def get_queryset(self):
		user = self.request.user
		return user.solved.all()


# Problem Views
class ProblemListView(APIView):
	permission_classes = [AllowAny]
	pagination_class = PageNumberPagination()
	def get(self, request: HttpRequest):
		problems = self.pagination_class.paginate_queryset(self.get_queryset(), request)
		serializer = serializers.ListProblemSerializer(problems, many=True)
		return OK(data=serializer.data)

	def get_queryset(self):
		topic = self.request.query_params.get("topic", "")
		difficulty = self.request.query_params.get("difficulty", "")
		difficulty = difficulty if not difficulty else (
			int(difficulty) if 0 < int(difficulty) < 4 else difficulty
		)
		search = self.request.query_params.get("search", "")
		print(f"query_string->\ntopic: {topic}\ndifficulty: {difficulty}\nsearch: {search}")

		filter_criteria = Q(topic__topic__icontains=topic)
		if difficulty:
			filter_criteria = filter_criteria & Q(difficulty__icontains=difficulty)
		search_criteria = Q(title__icontains=search) | Q(description__icontains=search)
		problems = models.Problem.objects.filter(filter_criteria).filter(search_criteria)
		print(problems)

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
	pagination_class = PageNumberPagination

	def post(self, request: HttpRequest, pk):
		comment = request.data.get("comment", "").strip()
		problem = get_or_404(models.Problem, id=pk)

		if not comment:
			return BAD_REQUEST({"error": "comment cannot be empty."})
		
		comment = models.Comment.objects.create(
			comment=comment,
			problem=problem,
			user=request.user)
		return OK()
	
	def get_queryset(self):
		return models.Comment.objects.filter(Q(problem__id=self.kwargs.get("pk")))
	
	def get_permissions(self):
		return [AllowAny()] if self.request.method == "GET" else [IsAuthenticated()]


# Topic Views
class TopicListView(generics.ListAPIView):
	# View to list all topics
	serializer_class = serializers.TopicSerializer
	pagination_class = TopicPagination
	queryset = models.Topic.objects.all()

# Test Case Views
class TestCaseListView(generics.ListAPIView):
	# View to list test cases for a specific problem
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
	async def post(self, request: HttpRequest, problem_id):
		queryset = models.TestCase.objects.filter(problem__id=problem_id)
		data = self.serializer_class(queryset, many=True).data
		# how the data will look like? this is important to know because
		#   we are gonna use this data in the code runner container.
		# or later in the container maybe we converted them using json.loads to get the actual dataStructure.
		print(data)
		python_file = request.data.get("python_file", "")
		if not python_file:
			return BAD_REQUEST({"error": "you didn't uploaded any file, or maybe you named it wrong in request body\n\
					   the name must be exactly like this-> 'python_file'."})
		utils.start_code_runner_container()
		with ThreadPoolExecutor() as executor:
			params = {
				"url":"http://127.0.0.1:{settigns.CODE_RUNNER_PORT}/run",
				"data": data,
				"files": python_file
				}
			feature = executor.submit(utils.send_post_request, **params)
			response = feature.result(timeout=settings.CODE_RUNNER_TIMEOUT)
	return OK(data=response.json())