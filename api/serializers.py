from rest_framework import serializers
from . import models

class UserSerializer(serializers.ModelSerializer):
	solved = serializers.IntegerField(help_text="solved problems count.")
	class Meta:
		model = models.CustomUser
		fields = "__all__"
		exclude = ["solved"]

class SolvedSerializer(serializers.Serializer):
	user_id = serializers.IntegerField(help_text="foreign key of the user solved the problem.")
	problem_id = serializers.IntegerField(help_text="foreign key of the user solved the problem.")


class ListProblemSerializer(serializers.ModelSerializer):
	likes = serializers.IntegerField(help_text="likes count.")
	class Meta:
		model = models.Problem
		fields = "__all__"
		exclude = ["template", "hint", "likes"]

class ProblemDetailSerializer(serializers.Serializer):
	likes = serializers.IntegerField(help_text="likes count.")
	class Meta:
		model = models.Problem
		fields = "__all__"
		exclude = ["likes"]

class TopicSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Topic
		fields = "__all__"

class CommentSerializser(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = models.Comment
		fields = "__all__"
		exclude = "problem"
