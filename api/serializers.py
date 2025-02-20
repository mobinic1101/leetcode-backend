from django.core.validators import MaxLengthValidator, MinLengthValidator
from rest_framework import serializers
from . import models


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Topic
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField(method_name="get_profile_pic")
    username = serializers.CharField(
        min_length=5,
        max_length=150,
        validators=[MaxLengthValidator, MinLengthValidator],
    )

    def __init__(self, *args, **kwargs):
        fields_include = kwargs.pop("fields", [])

        # filter fields based on quick_user_fields:
        if fields_include:
            fields = {
                key: val for key, val in self.fields.items() if key in fields_include
            }
            self.fields = fields
        super(UserSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CustomUser
        exclude = ["password", "solved"]

    def get_profile_pic(self, user):
        return user.get_image_url()


class ListProblemSerializer(serializers.ModelSerializer):
    topics = serializers.SerializerMethodField(method_name="get_topics")

    class Meta:
        model = models.Problem
        exclude = ["template", "hint"]

    def get_topics(self, problem: models.Problem):
        topics = problem.topics.all()
        return TopicSerializer(topics, many=True).data


class SolvedSerializer(serializers.Serializer):
    id_ = serializers.SerializerMethodField(method_name="get_id")
    title = serializers.SerializerMethodField(method_name="get_title")
    topics = serializers.SerializerMethodField(method_name="get_topics")
    description = serializers.SerializerMethodField(method_name="get_desc")

    def get_id(self, problem: models.Problem):
        return problem.id

    def get_title(self, problem: models.Problem):
        return problem.title

    def get_topics(self, problem: models.Problem):
        topics = problem.topics.all()
        return TopicSerializer(topics, many=True).data

    def get_desc(self, problem: models.Problem):
        return problem.description


class ProblemDetailSerializer(serializers.ModelSerializer):
    topics = serializers.SerializerMethodField(method_name="get_topics")

    class Meta:
        model = models.Problem
        fields = "__all__"

    def get_topics(self, problem: models.Problem):
        topics = problem.topics.all()
        return TopicSerializer(topics, many=True).data


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Comment
        exclude = ["problem"]


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TestCase
        exclude = ["problem"]

