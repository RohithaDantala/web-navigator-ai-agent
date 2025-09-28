# services/memory_service.py
import sqlite3
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MemoryService:
    def __init__(self, db_path: str = "web_navigator.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    instruction TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    async def store_session_data(self, session_id: str, instruction: str, result: Dict[str, Any]):
        """Store session data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (session_id, instruction, result)
                VALUES (?, ?, ?)
            """, (session_id, instruction, json.dumps(result)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store session data: {e}")

    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT instruction, result, created_at
                FROM sessions
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (session_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                history.append({
                    "instruction": row[0],
                    "result": json.loads(row[1]),
                    "timestamp": row[2]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []

    async def store_task(self, task_id: str, instruction: str, plan: List[Dict[str, Any]]):
        """Store task plan"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO tasks (task_id, instruction, plan)
                VALUES (?, ?, ?)
            """, (task_id, instruction, json.dumps(plan)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store task: {e}")

    async def update_task_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None):
        """Update task status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if result:
                cursor.execute("""
                    UPDATE tasks 
                    SET status = ?, result = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """, (status, json.dumps(result), task_id))
            else:
                cursor.execute("""
                    UPDATE tasks 
                    SET status = ?
                    WHERE task_id = ?
                """, (status, task_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")