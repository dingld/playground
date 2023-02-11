import os
import scraperx


def get_project_path():
    path = scraperx.__file__
    return os.path.dirname(os.path.dirname(path))
