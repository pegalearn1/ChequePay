import threading

_thread_locals = threading.local()

class AttachRequestToDBRouterMiddleware:
    """
    Middleware to attach the request object to thread-local storage.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store the request in thread-local storage
        _thread_locals.request = request
        response = self.get_response(request)
        return response

def get_current_request():
    """
    Helper function to retrieve the current request object from thread-local storage.
    """
    return getattr(_thread_locals, 'request', None)
