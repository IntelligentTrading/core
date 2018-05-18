from rest_framework.pagination import CursorPagination

# http://www.django-rest-framework.org/api-guide/pagination/#cursorpagination

class StandardResultsSetPagination(CursorPagination):
    page_size = 50
    ordering = ('-timestamp', '-id')
    page_size_query_param = 'page_size'
    max_page_size = 10000

class OneRecordPagination(CursorPagination):
    page_size = 1
    ordering = ('-timestamp', '-id')
    page_size_query_param = 'page_size'
    max_page_size = 10000
