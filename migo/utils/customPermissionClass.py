from rest_framework import permissions

class NotDjangoAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if  request.user.is_anonymous and request.user.is_admin:
            return False
        return True
    
class SignUpProcessCompleted(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.sign_up_steps != 'Wander List Set':
            return False
        return True

class IsHost(permissions.BasePermission):

    def has_permission(self, request, view):
        if  not request.user.is_host:
            return False
        return True