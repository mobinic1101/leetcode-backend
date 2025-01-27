from django.core.validators import MaxLengthValidator, MinLengthValidator
from rest_framework import serializers
from . import models


class UserSerializer(serializers.ModelSerializer):
    solved = serializers.SerializerMethodField(method_name="get_solved_count")
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    username = serializers.CharField(
        min_length=5,
        max_length=150,
        validators=[MaxLengthValidator, MinLengthValidator],
    )

    def __init__(self, *args, **kwargs):
        quick_user_fields = kwargs.pop("fields", [])

        # filter fields based on quick_user_fields:
        if quick_user_fields:
            fields = {
                key: val for key, val in self.fields.items() if key in quick_user_fields
            }
            self.fields = fields
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CustomUser
        exclude = ["password"]

    def get_solved_count(self, user):
        return user.solved.all().count()

    def get_profile_pic(self, user):
        return user.get_image_url()


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
    description = serializers.SerializerMethodField(method_name="get_desc")

    def get_id(self, problem: models.Problem):
        return problem.id

    def get_title(self, problem: models.Problem):
        return problem.title

    def get_topic(self, problem: models.Problem):
        return problem.topic.topic

    def get_desc(self, problem: models.Problem):
        return problem.description


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Topic
        fields = "__all__"


class ProblemDetailSerializer(serializers.ModelSerializer):
    topic = TopicSerializer()

    class Meta:
        model = models.Problem
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Comment
        exclude = ["problem"]


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TestCase
        exclude = ["problem"]
