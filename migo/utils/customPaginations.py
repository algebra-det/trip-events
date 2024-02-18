from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework.response import Response
from django.conf import settings

class CustomPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('status', True), # add the 'custom' field  
            ('page_size', settings.REST_FRAMEWORK['PAGE_SIZE']),
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),            
        ]))