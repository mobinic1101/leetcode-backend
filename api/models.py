from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# enums
class Difficulty(models.IntegerChoices):
    easy = 1, "Easy"
    medium = 2, "Medium"
    hard = 3, "Hard"


class Topic(models.Model):
    topic = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.topic


class Problem(models.Model):
    title = models.CharField(max_length=300, unique=True)
    description = models.TextField(null=True, blank=True)
    template = models.TextField(null=True, blank=True)
    hint = models.CharField(max_length=500, blank=True, null=True)
    allowed_imports = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="comma-separated list of allowed imports",
    )
    topics = models.ManyToManyField(to=Topic, blank=True)
    difficulty = models.IntegerField(
        null=True, default=None, choices=Difficulty.choices
    )

    def __str__(self) -> str:
        return self.title


class CustomUser(AbstractUser):
    profile_pic = models.ImageField(
        upload_to="profile_pics/",
        default="profile_pics/default.svg",
        null=True,
        blank=True,
    )
    solved = models.ManyToManyField(
        to="Problem", blank=True, through="Solved", related_name="solved_problems"
    )
    solved_count = models.IntegerField(default=0, blank=True, db_index=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def get_image_url(self):
        return settings.DRF_HOST + self.profile_pic.url

    def add_solved_problem(self, problem: Problem):
        Solved.objects.create(user=self, problem=problem)
        self.solved_count += 1
        self.save()

    def __str__(self) -> str:
        return self.username


class Solved(models.Model):
    user = models.ForeignKey(
        to="CustomUser", on_delete=models.CASCADE, related_name="user"
    )
    problem = models.ForeignKey(to="Problem", on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "problem"]


class Comment(models.Model):
    comment = models.TextField(blank=True)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(to=Problem, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment


class TestCase(models.Model):
    problem = models.ForeignKey(to=Problem, on_delete=models.CASCADE)
    input = models.TextField(db_column="input", unique=True, blank=True)
    expected = models.TextField(blank=True)
