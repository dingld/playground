import logging
import os

import yaml

from scraperx.utils.misc import get_project_path

_DEFAULT_CONFIG_DIR = os.path.join(get_project_path(), "configs")


def read_config_all(path: str = "", suffix: str = ".yaml") -> dict:
    paths = []
    if path:
        paths = [path]
    if not path:
        for root, dirs, files in os.walk(_DEFAULT_CONFIG_DIR):
            for filename in files:
                if not filename.endswith(suffix):
                    continue
                paths.append(os.path.join(root, filename))
    configs = dict()
    for filepath in paths:
        configs.update(read_single_config(filepath))
    return configs


def read_single_config(path: str) -> dict:
    with open(path) as fp:
        return yaml.safe_load(fp)


def read_config_key(key: str, path: str = ""):
    d = read_config_all(path)
    return d.get(key, "")


def set_config_level_fmt():
    logging.basicConfig(
        level=read_config_key("log.level"),
        format=read_config_key("log.fmt")
    )
