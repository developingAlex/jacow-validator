import json
from .models import Log
from docx import Document


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


# TODO Make sure editing copy of data, not original data
def json_serialise(x):
    json_data = {}
    for i, data in x.items():
        keys_to_delete = []
        if isinstance(data, Log) or i == 'metadata' or i == 'doc':
            json_data[i] = ''
            # no nothings
        elif isinstance(data, dict):
            for key, value in data.items():
                if not is_jsonable(value):
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del data[key]
            json_data[i] = json.dumps(data)
        elif isinstance(data, list):
            for value in data:
                if not is_jsonable(value):
                    keys_to_delete.append(value)
            for key in keys_to_delete:
                data.remove(key)
            json_data[i] = json.dumps(data)
        else:
            json_data[i] = json.dumps(data)

    return json_data
