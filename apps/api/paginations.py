from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination


class StandardResultsSetPagination(CursorPagination):
    page_size = 50
    ordering = '-timestamp'

class OneRecordPagination(CursorPagination):
    page_size = 1
    ordering = '-timestamp'
    