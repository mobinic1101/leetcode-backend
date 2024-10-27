from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework.authtoken.views import obtain_auth_token
from . import auth
from . import views

DEBUG, MEDIA_URL, MEDIA_ROOT = (settings.DEBUG, settings.MEDIA_URL, settings.MEDIA_ROOT)

urlpatterns = [
	path("api-token-auth/", obtain_auth_token),
	path("sign-up/", auth.sign_up, name="sign_up"),

    # User-related paths
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("users/me/solved-problems/", views.UserSolvedProblemsView.as_view(), name="user_solved_problems"),

    # Problem-related paths
    path("problems/", views.ProblemListView.as_view(), name="problem_list"),  # List all problems
    path("problems/<int:pk>/", views.ProblemDetailView.as_view(), name="problem_detail"),  # Retrieve a specific problem
    path("problems/<int:pk>/comments/", views.ProblemCommentView.as_view(), name="problem_comments"),  # Comments on a specific problem

    # Topic-related paths
    path("topics/", views.TopicListView.as_view(), name="topic_list"),  # List all topics
    
    # Test case-related paths
    path("problems/<int:problem_id>/testcases/", views.TestCaseListView.as_view(), name="testcase_list"),  # List all test cases for a specific problem
    path("problems/<int:problem_id>/run/", views.CodeRunningView.as_view(), name="run_code"),  # Run a code snippet for a specific problem

]

print(DEBUG)
if DEBUG:
    urlpatterns += static(prefix=MEDIA_URL, document_root=MEDIA_ROOT)