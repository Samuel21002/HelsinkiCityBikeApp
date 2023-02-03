from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

AUTH_EXEMPT_ROUTES = ('captcha-image', 'login', 'captcha')

class RejectAnonymousUsersMiddleware(MiddlewareMixin):
    """ By default, the apps require authentication """

    def process_view(self, request, view_func, view_args, view_kwargs):
        current_route_name = resolve(request.path_info).url_name

        if request.user.is_authenticated:
            return

        if current_route_name in AUTH_EXEMPT_ROUTES:
            return
            
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *view_args, **view_kwargs)