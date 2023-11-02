from django.shortcuts import redirect
from functools import wraps
from django.utils.decorators import method_decorator

def redirect_if_logged_in(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

