class AttachRequestToDBRouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.db.models.base import ModelBase

        print("Attaching request to ModelBase._hints")  # Debugging output

        def custom_hints(model, **kwargs):
            return {'request': request}

        ModelBase._hints = custom_hints

        response = self.get_response(request)

        del ModelBase._hints
        return response
