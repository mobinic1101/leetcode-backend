from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import auth, views


urlpatterns = [
	path("api-token-auth", obtain_auth_token),
	path("sign-up", auth.sign_up, name="sign_up"),

    # User-related paths
    path("users/me/", views.UserDetailView.as_view(), name="user_detail"),
    path("users/me/problems/", views.UserSolvedProblemsView.as_view(), name="user_solved_problems"),
    path("users/me/like/<int:problem_id>/", views.UserLikeProblemView.as_view(), name="user_like_problem"),

    # Problem-related paths
    path("problems/", views.ProblemListView.as_view(), name="problem_list"),  # List all problems
    path("problems/<int:pk>/", views.ProblemDetailView.as_view(), name="problem_detail"),  # Retrieve a specific problem
    path("problems/<int:pk>/comments/", views.ProblemCommentView.as_view(), name="problem_comments"),  # Comments on a specific problem

    # Topic-related paths
    path("topics/", views.TopicListView.as_view(), name="topic_list"),  # List all topics
    path("topics/<int:topic_id>/problems/", views.TopicProblemsView.as_view(), name="topic_problems"),  # List problems by topic

    # Difficulty-related paths
    path("problems/difficulty/<int:difficulty>/", views.DifficultyProblemsView.as_view(), name="difficulty_problems"),  # List problems by difficulty

    # Test case-related paths
    path("problems/<int:problem_id>/testcases/", views.TestCaseListView.as_view(), name="testcase_list"),  # List all test cases for a specific problem
]