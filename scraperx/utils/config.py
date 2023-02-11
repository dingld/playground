import os

import yaml
from scraperx.utils.misc import get_project_path


def read_config_all(path: str = "") -> dict:
    if not path:
        path = "configs/settings.yaml"
    with open(os.path.join(get_project_path(), path)) as fp:
        return yaml.safe_load(fp)


def read_config_key(key: str, path: str = ""):
    d = read_config_all(path)
    return d.get(key, "")
