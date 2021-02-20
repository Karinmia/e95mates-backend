from rest_framework.renderers import JSONRenderer
from rest_framework.views import exception_handler

from django.utils.translation import gettext as _


class MyJSONRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data:
            if 'error' not in data:
                if isinstance(data, dict):
                    data['error'] = False

        return super(MyJSONRenderer, self).render(data, accepted_media_type, renderer_context)


def custom_exception_handler(exc, context):
    """
    Call REST framework's default exception handler first,
    to get the standard error response.
    """

    helper = ["detail", "phone", "full_name", "photo", "passcode"]

    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None:
        try:
            exception = exc.detail
        except:
            response.data['details'] = str(exc)
            response.data['status'] = 404
        else:
            error = {}  # default errors obj
            response.data['error'] = True

            if 'non_field_errors' in exception:
                details = exception.pop('non_field_errors')
                error['non_field_errors'] = _(details)

            if 'detail' in response.data:
                _detail = response.data.pop('detail')
                if isinstance(_detail, list):
                    error = _(_detail[0])
                else:
                    error = _(_detail)
            else:
                # Check models and serializers fields' errors
                key_fields = list(exception.keys())
                for key_field in key_fields:
                    if key_field in helper:
                        key_error = response.data.pop(key_field)
                        if isinstance(key_error, list):
                            error[key_field] = _(key_error[0])
                        else:
                            error[key_field] = _(key_error)

            response.data['details'] = error
            response.data['status'] = int(exception['status']) if "status" in exception else response.status_code

    return response
