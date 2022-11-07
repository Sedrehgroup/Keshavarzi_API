from collections import OrderedDict
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NotePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 25

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        if count is 0:
            raise NotFound({"Notes": "We didn't find any matching note."})
        return Response(OrderedDict([
            ('count', count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
