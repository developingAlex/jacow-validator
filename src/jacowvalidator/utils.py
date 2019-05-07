import json
from .models import Log


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


def json_serialise(x):
    json_data = {}
    for i, data in x.items():
        # ignore non serialisable data
        if isinstance(data, Log) or i == 'metadata' or i == 'doc':
            continue
        else:
            json_data[i] = json.dumps(data)

    return json_data
