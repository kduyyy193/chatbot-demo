import sqlite3
import logging
from contextlib import contextmanager
from typing import Iterator

from src.config.settings import settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DB_PATH = settings.DB_PATH


class DatabaseConnection:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fine_tuned_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT FALSE
                )
            """
            )
            conn.commit()
        logger.info("Database initialized")
