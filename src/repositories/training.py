from typing import List, Dict, Optional
from src.db.connection import DatabaseConnection
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TrainingDataRepository:
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn

    def save_training_data(self, content: str) -> Optional[int]:
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO training_data (content) VALUES (?)", (content,))
            conn.commit()
            last_id = cursor.lastrowid
            logger.info(f"Saved training data with ID: {last_id}")
            return last_id

    def get_all_training_data(self) -> List[Dict[str, str]]:
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM training_data")
            rows = cursor.fetchall()
        return [{"role": "system", "content": row[0]} for row in rows]

    def save_fine_tuned_model_to_db(self, model_name: str) -> None:
        try:
            with self.db_conn.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE fine_tuned_models SET is_active = 0")
                cursor.execute(
                    "INSERT INTO fine_tuned_models (model_name, is_active) VALUES (?, 1)",
                    (model_name,),
                )

                conn.commit()
                conn.close()
            logger.info(f"Saved fine-tuned model to DB: {model_name}")
        except Exception as e:
            logger.error(f"Error saving model to DB: {str(e)}")
            raise

    def get_current_model_from_db(self) -> str:
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT model_name FROM fine_tuned_models WHERE is_active = 1 LIMIT 1")
            result = cursor.fetchone()
            if result:
                return result["model_name"]
            logger.warning("No active model found in DB, using default")
            return "gpt-4o-mini-2024-07-18"
