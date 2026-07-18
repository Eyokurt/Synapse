import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class SQLiteMemory:
    def __init__(self, db_path: str, session_id: str):
        self.db_path = db_path
        self.session_id = session_id
        # Use check_same_thread=False to allow usage across different threads
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                tool_calls TEXT,
                tool_call_id TEXT,
                timestamp DATETIME
            )
        """)
        self.conn.commit()

    def add_message(self, message: Dict[str, Any]) -> Optional[int]:
        role = message.get("role")
        content = message.get("content")
        tool_calls = message.get("tool_calls")
        tool_call_id = message.get("tool_call_id")
        
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None

        cursor = self.conn.cursor()
        # Basic deduplication: check last message
        cursor.execute("""
            SELECT role, content, tool_calls, tool_call_id 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp DESC, id DESC LIMIT 1
        """, (self.session_id,))
        last_msg = cursor.fetchone()

        if last_msg:
            last_role, last_content, last_tool_calls, last_tool_call_id = last_msg
            if (last_role == role and 
                last_content == content and 
                last_tool_calls == tool_calls_json and
                last_tool_call_id == tool_call_id):
                return None 
        
        cursor.execute("""
            INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.session_id, role, content, tool_calls_json, tool_call_id, datetime.now(timezone.utc).isoformat()))
        self.conn.commit()
        return cursor.lastrowid

    def get_messages(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, role, content, tool_calls, tool_call_id 
            FROM messages 
            WHERE session_id = ? 
            ORDER BY timestamp ASC, id ASC
        """, (self.session_id,))
        rows = cursor.fetchall()

        messages = []
        for row in rows:
            msg_id, role, content, tool_calls, tool_call_id = row
            msg = {"role": role}
            if content is not None:
                msg["content"] = content
            if tool_calls is not None:
                msg["tool_calls"] = json.loads(tool_calls)
            if tool_call_id is not None:
                msg["tool_call_id"] = tool_call_id
            messages.append(msg)
        return messages

    def delete_message(self, msg_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE id = ? AND session_id = ?", (msg_id, self.session_id))
        self.conn.commit()

    def clear(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (self.session_id,))
        self.conn.commit()
