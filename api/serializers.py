from rest_framework import serializers
from . import models

class SolvedSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(help_text="foreign key of the user solved the problem.")
	problem_id = serializers.IntegerField(help_text="foreign key of the problem solved by user.")

class LikedSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(help_text="foreign key of the user liked the problem.")
	problem_id = serializers.IntegerField(help_text="foreign key of the problem liked by user.")

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

class ProblemDetailSerializer(serializers.Serializer):
	likes = SolvedSerializer(many=True)
	class Meta:
		model = models.Problem
		fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Topic
		fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = models.Comment
		exclude = ["problem"]
