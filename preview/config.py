import json
import pkg_resources

data = pkg_resources.resource_string(__name__, "config.json")
config = json.loads(data)