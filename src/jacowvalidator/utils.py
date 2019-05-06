import json
from .models import Log


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
        # keys_to_keep = []
        if isinstance(data, Log) or i == 'metadata' or i == 'doc':
            continue
        # elif isinstance(data, dict):
        #     for key, value in data.items():
        #         if not key == 'text' and is_jsonable(value):
        #             keys_to_keep.append(key)
        #     json_data[i] = json.dumps({key:value for key, value in data.items() if key in keys_to_keep})
        # elif isinstance(data, list):
        #     for value in data:
        #         if is_jsonable(value):
        #             keys_to_keep.append(value)
        #     json_data[i] = json.dumps([value for value in data if keys_to_keep in keys_to_keep])
        else:
            json_data[i] = json.dumps(data)

    return json_data
