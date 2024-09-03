from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import serializers
from . import models


# User Views
class UserDetailView(generics.RetrieveAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = serializers.UserSerializer

	def get_object(self):
		primary_key = int(self.kwargs.get("pk"))
		try:
			user = models.CustomUser.objects.get(id=primary_key)
		except:
			return Response(data={"error": "user does not exist."}, status=status.HTTP_404_NOT_FOUND)
		return user


class UserSolvedProblemsView(generics.ListAPIView):
	def get_queryset(self):
		pass


class UserLikeProblemView(APIView):
	"""
		responsible for liking a problem and get the liked problems of a user.
	"""
	pass


# Problem Views
class ProblemListView(APIView):
	pass  # View to list all problems


class ProblemDetailView(APIView):
	pass  # View to retrieve details of a specific problem


class ProblemCommentView(APIView):
	pass  # View to handle comments on a problem (GET and POST)


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
