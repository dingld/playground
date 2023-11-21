import logging
import os

import yaml

from scraperx.utils.misc import get_project_path

_DEFAULT_CONFIG_DIR = os.path.join(get_project_path(), "configs")
_CONFIGS_CACHE = dict()


def scan_files_in_dir(path: str, suffix: str):
    for root, dirs, files in os.walk(path):
        for filename in files:
            if suffix and not filename.endswith(suffix):
                continue
            filepath = os.path.join(root, filename)
            yield filepath


def read_config_all_yaml(path: str = "", suffix: str = ".yaml") -> dict:
    if _CONFIGS_CACHE.get(path):
        return _CONFIGS_CACHE.get(path, dict())

    paths = []
    if path:
        paths = [path]
    if not path:
        for filepath in scan_files_in_dir(_DEFAULT_CONFIG_DIR, suffix):
            if filepath.endswith("default.yaml"):
                paths = [filepath] + paths
            else:
                paths.append(filepath)
    configs = dict()
    for filepath in paths:
        configs.update(read_single_config(filepath) or dict())
    _CONFIGS_CACHE[path] = configs
    return configs.copy()


def read_single_config(path: str) -> dict:
    with open(path) as fp:
        return yaml.safe_load(fp)


def read_config_key(key: str, path: str = ""):
    d = read_config_all_yaml(path)
    return d.get(key, "")


def set_config_level_fmt():
    logging.basicConfig(
        level=read_config_key("log.level"),
        format=read_config_key("log.fmt")
    )
