from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
	solved = serializers.SerializerMethodField(method_name="get_solved_count")

	class Meta:
		model = models.CustomUser
		exclude = ['password']

	def get_solved_count(self, user):
		return user.solved.all().count()


class ListProblemSerializer(serializers.ModelSerializer):
	likes = serializers.SerializerMethodField(method_name="get_likes")

	class Meta:
		model = models.Problem
		exclude = ["template", "hint"]

	def get_likes(self, problem):
		return problem.likes.all().count()


class SolvedSerializer(serializers.Serializer):
	problem = serializers.SerializerMethodField(method_name="get_basic_problem_details")

	def get_basic_problem_details(self, problem: models.Problem):
		data = {
			"id": problem.id,
			"title": problem.title
		}
		return data

class LikedSerializer(SolvedSerializer):
	pass

class ProblemDetailSerializer(serializers.Serializer):
	likes = serializers.SerializerMethodField(method_name="get_likes")
	class Meta:
		model = models.Problem
		fields = '__all__'
	
	def get_likes(self, problem):
		return problem.likes.all().count()

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Topic
		fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = models.Comment
		exclude = ["problem"]
