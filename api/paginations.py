from rest_framework.pagination import PageNumberPagination

class TopicPagination(PageNumberPagination):
    page_size = 100