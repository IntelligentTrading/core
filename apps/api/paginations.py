from rest_framework.pagination import CursorPagination

# http://www.django-rest-framework.org/api-guide/pagination/#cursorpagination

class StandardResultsSetPagination(CursorPagination):
    page_size = 50
    ordering = '-timestamp'

class OneRecordPagination(CursorPagination):
    page_size = 1
    ordering = '-timestamp'
