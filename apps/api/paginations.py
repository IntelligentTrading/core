from rest_framework.pagination import CursorPagination

# http://www.django-rest-framework.org/api-guide/pagination/#cursorpagination

class StandardResultsSetPagination(CursorPagination):
    page_size = 50
    ordering = ('-timestamp', '-id')
    page_size_query_param = 'page_size'
    max_page_size = 10000

class StandardResultsSetPaginationOnlyTimestamp(CursorPagination):
    page_size = 50
    ordering = ('-timestamp')
    page_size_query_param = 'page_size'
    max_page_size = 10000