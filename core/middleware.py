# core/middleware.py
class UserRoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.user.is_authenticated:
            from core.models import AllowedEmail
            try:
                allowed = AllowedEmail.objects.get(email=request.user.email)
                request.user.role = allowed.role
                request.user.can_edit = allowed.role in ['admin', 'user']
            except AllowedEmail.DoesNotExist:
                request.user.role = 'viewer'
                request.user.can_edit = False
        return self.get_response(request)