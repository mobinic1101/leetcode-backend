from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.http import HttpRequest

from . import serializers
from . import models


def DOES_NOT_EXIST(data={"error": "does not exist."}, status=status.HTTP_404_NOT_FOUND):
	return Response(data=data, status=status)

def BAD_REQUEST(data: dict, status=status.HTTP_400_BAD_REQUEST):
	return Response(data=data, status=status)

def OK(data, status=status.HTTP_200_OK):
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
		print(f"type: {type(data)} =>", data)
		serializer = self.serializer_class(instance=obj, data=data)

		# Error checking:
		fields_to_restrict = ["is_staff", "is_superuser"]
		for key in fields_to_restrict:
			if key in data:
				return BAD_REQUEST({
					"error":f"cannot modify these properties: {', '.join(fields_to_restrict)}"
					})
		if not serializer.is_valid():
			return Response(data=serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
		
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_object(self, pk):
		try:
			user = models.CustomUser.objects.get(id=pk)
		except models.CustomUser.DoesNotExist:
			return DOES_NOT_EXIST
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
# I knew i could use generics.ListAPIView here, i just wanted to do it manually.
class ProblemListView(APIView):
	permission_classes = [AllowAny]
	pagination_class = PageNumberPagination()
	def get(self, request: HttpRequest):
		query_params = request.query_params
		print(query_params)
		return OK({})

	def get_queryset(self):
		topic = self.request.query_params.get("topic")
		difficulty = self.request.query_params.get("difficulty")
		search = self.request.query_params.get("search")



class ProblemDetailView(APIView):
	pass  # View to retrieve details of a specific problem


class ProblemCommentView(APIView):
	pass  # View to handle comments on a problem (GET and POST)


class ProblemLikeView(APIView):
	pass # responsible for displaying likes on a specific problem.


# Topic Views
class TopicListView(APIView):
	pass  # View to list all topics


class TopicProblemsView(APIView):
	pass  # View to list problems under a specific topic


# Difficulty Views
class DifficultyProblemsView(APIView):
	pass  # View to list problems by difficulty


# Test Case Views
class TestCaseListView(APIView):
	pass  # View to list test cases for a specific problem


