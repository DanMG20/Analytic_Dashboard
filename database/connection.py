import sqlite3
from contextlib import contextmanager
from datetime import date
from typing import Generator


class DatabaseManager:
    """
    Manages SQLite database connections using the Context Manager pattern.
    """

    def __init__(self, db_path: str):
        self._db_path = db_path

        sqlite3.register_adapter(date, lambda d: d.isoformat())

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Yields a transactional SQLite connection.
        """
        connection = sqlite3.connect(
            self._db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        except sqlite3.Error:
            connection.rollback()
            raise
        finally:
            connection.commit()
            connection.close()
