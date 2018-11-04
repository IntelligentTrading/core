from rest_framework import permissions
from settings import REST_API_SECRET_KEY

class RestAPIPermission(permissions.BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        return True
        api_key = request.META.get('HTTP_API_KEY', '')
        return api_key == REST_API_SECRET_KEY # Allow access if True

