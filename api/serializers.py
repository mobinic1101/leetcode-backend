from rest_framework import serializers
from . import models
from .utils import convert_literal


class UserSerializer(serializers.ModelSerializer):
	solved = serializers.SerializerMethodField(method_name="get_solved_count")

	class Meta:
		model = models.CustomUser
		exclude = ['password']

	def get_solved_count(self, user):
		return user.solved.all().count()


class ListProblemSerializer(serializers.ModelSerializer):
	topic = serializers.SerializerMethodField(method_name="get_topic")
	class Meta:
		model = models.Problem
		exclude = ["template", "hint"]

	def get_topic(self, problem: models.Problem):
		return problem.topic.topic


class SolvedSerializer(serializers.Serializer):
	id_ = serializers.SerializerMethodField(method_name="get_id")
	title = serializers.SerializerMethodField(method_name="get_title")
	topic = serializers.SerializerMethodField(method_name="get_topic")

	def get_id(self, problem: models.Problem):
		return problem.id

	def get_title(self, problem: models.Problem):
		return problem.title

	def get_topic(self, problem: models.Problem):
		return problem.topic.topic

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Topic
		fields = "__all__"

class ProblemDetailSerializer(serializers.ModelSerializer):
	topic = TopicSerializer()
	class Meta:
		model = models.Problem
		fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = models.Comment
		exclude = ["problem"]

class TestCaseSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.TestCase
		exclude = ["problem"]
