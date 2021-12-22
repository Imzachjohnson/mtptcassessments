import json

from bson import json_util
from bson.json_util import dumps


def parse_json(data, dashboard: bool = False):

    if dashboard:
        data = json.loads(json_util.dumps(data))
        print(data)
        for d in data:
            print(d)
            d["x"] = d.pop("_id")
        print(data)
        return data

    return json.loads(json_util.dumps(data))
