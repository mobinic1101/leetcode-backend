from rest_framework.pagination import PageNumberPagination

class TopicPagination(PageNumberPagination):
    page_size = 100


class ProblemListViewPagination(PageNumberPagination):
    page_size = 15