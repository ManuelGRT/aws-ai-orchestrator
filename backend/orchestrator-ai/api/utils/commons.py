from datetime import datetime
from api.schemas.errors import ErrorResponse

RESPONSES = {
    400: {'model': ErrorResponse},
    401: {'model': ErrorResponse},
    403: {'model': ErrorResponse},
    500: {'model': ErrorResponse}
}


class ObjectToDictConverter:
    @staticmethod
    def to_dict(obj):
        if isinstance(obj, (int, float, bool, str, type(None))):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [ObjectToDictConverter.to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: ObjectToDictConverter.to_dict(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            obj_dict = {key: ObjectToDictConverter.to_dict(value) for key, value in obj.__dict__.items() if
                        not key.startswith("_")}
            return obj_dict
        else:
            return None