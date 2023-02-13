import os
import sqlite3
from sqlite3 import Connection
from time import time
from typing import List

import pandas as pd

from scraperx.utils.misc import get_project_path

_gloable_session: Connection = None


def init_sqlite3_conn(extension_path: str = None):
    global _gloable_session
    if not _gloable_session:
        if extension_path is None:
            extension_path = os.path.join(get_project_path(), "extensions/sqlite3/html0")
        conn = sqlite3.connect(':memory:')
        global _LOADED
        conn.enable_load_extension(True)
        conn.load_extension(extension_path)
        _gloable_session = conn
        df = pd.DataFrame([{"source": "source", "base_url": "base_url", "created_at": int(time())}])
        df.to_sql("response", con=conn, if_exists="replace")
    return _gloable_session


def init_sqlite3_source(conn: Connection, source: str, base_url, name: str = "response"):
    clear_sqlite3_parser(conn, base_url, 60)
    df = pd.DataFrame([{"source": source, "base_url": base_url, "created_at": int(time())}])
    df.to_sql(name, con=conn, if_exists="append")


def query_sqlite3_parser(conn: Connection, sql) -> List[dict]:
    df = pd.read_sql(sql=sql, con=conn)
    return df.to_dict("records")


def clear_sqlite3_parser(conn: Connection, base_url: str, seconds: int = 60):
    conn.execute("delete from response where created_at < {0} or base_url = '{1}'".format(int(time() - seconds), base_url))
    conn.commit()
