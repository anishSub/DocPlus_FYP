import traceback
from superAdmin.models import ErrorLog

class ExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # This method is called when a view raises an exception
        
        # Get the full stack trace
        stack_trace = traceback.format_exc()

        # Get the user if authenticated
        user = request.user if request.user.is_authenticated else None

        # Create the ErrorLog entry
        ErrorLog.objects.create(
            message=str(exception),
            stack_trace=stack_trace,
            path=request.path,
            method=request.method,
            user=user
        )

        # Return None to allow standard Django error handling (e.g. 500 page)
        return None
