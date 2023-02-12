import os
import sqlite3
from sqlite3 import Connection
from typing import List

import pandas as pd

from scraperx.utils.misc import get_project_path


def get_sqlite3_parser(extension_path: str = None):
    if extension_path is None:
        extension_path = os.path.join(get_project_path(), "extensions/sqlite3/html0")
    conn = sqlite3.connect(':memory:')
    conn.enable_load_extension(True)
    conn.load_extension(extension_path)


def init_sqlite3_parser(conn: Connection, source: str, base_url, name: str = "response"):
    df = pd.DataFrame([{"source": source, "base_url": base_url}])
    df.to_sql(name, con=conn)


def query_sqlite3_parser(conn: Connection, sql) -> List[dict]:
    df = pd.read_sql(sql=sql, con=conn)
    return df.to_dict("records")
