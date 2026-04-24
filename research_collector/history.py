"""Search history management with SQLite."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class HistoryManager:
    """Manage search history with SQLite database."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize history manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path.home() / ".research-collector" / "history.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Searches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                from_date TEXT NOT NULL,
                to_date TEXT NOT NULL,
                sources TEXT,
                depth TEXT DEFAULT 'default',
                result_count INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER NOT NULL,
                item_id TEXT NOT NULL,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT,
                author TEXT,
                published_date TEXT,
                score REAL,
                FOREIGN KEY (search_id) REFERENCES searches (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_search(
        self,
        topic: str,
        from_date: str,
        to_date: str,
        sources: Optional[List[str]] = None,
        depth: str = "default",
        result_count: int = 0,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add a search to history.
        
        Args:
            topic: Search topic
            from_date: Start date ISO string
            to_date: End date ISO string
            sources: List of sources used
            depth: Search depth
            result_count: Number of results
            metadata: Additional metadata
        
        Returns:
            Search ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sources_json = json.dumps(sources) if sources else None
        metadata_json = json.dumps(metadata) if metadata else None
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO searches (topic, from_date, to_date, sources, depth, result_count, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (topic, from_date, to_date, sources_json, depth, result_count, timestamp, metadata_json))
        
        search_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return search_id
    
    def add_results(self, search_id: int, results: List[Dict]) -> None:
        """Add results for a search.
        
        Args:
            search_id: Search ID
            results: List of result items
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in results:
            cursor.execute("""
                INSERT INTO results (search_id, item_id, title, source, url, author, published_date, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                search_id,
                item.get('id', ''),
                item.get('title', ''),
                item.get('source', ''),
                item.get('url', ''),
                item.get('author', ''),
                item.get('published_date', ''),
                item.get('score', 0)
            ))
        
        conn.commit()
        conn.close()
    
    def get_search_history(self, limit: int = 50) -> List[Dict]:
        """Get search history.
        
        Args:
            limit: Maximum number of searches to return
        
        Returns:
            List of search records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, topic, from_date, to_date, sources, depth, result_count, timestamp, metadata
            FROM searches
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        searches = []
        for row in cursor.fetchall():
            sources = json.loads(row[4]) if row[4] else []
            metadata = json.loads(row[8]) if row[8] else {}
            
            searches.append({
                'id': row[0],
                'topic': row[1],
                'from_date': row[2],
                'to_date': row[3],
                'sources': sources,
                'depth': row[5],
                'result_count': row[6],
                'timestamp': row[7],
                'metadata': metadata
            })
        
        conn.close()
        return searches
    
    def get_search_results(self, search_id: int) -> List[Dict]:
        """Get results for a specific search.
        
        Args:
            search_id: Search ID
        
        Returns:
            List of result items
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT item_id, title, source, url, author, published_date, score
            FROM results
            WHERE search_id = ?
            ORDER BY score DESC
        """, (search_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'source': row[2],
                'url': row[3],
                'author': row[4],
                'published_date': row[5],
                'score': row[6]
            })
        
        conn.close()
        return results
    
    def delete_search(self, search_id: int) -> bool:
        """Delete a search and its results.
        
        Args:
            search_id: Search ID
        
        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete results first
        cursor.execute("DELETE FROM results WHERE search_id = ?", (search_id,))
        result_count = cursor.rowcount
        
        # Delete search
        cursor.execute("DELETE FROM searches WHERE id = ?", (search_id,))
        search_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return search_count > 0
    
    def clear_history(self) -> int:
        """Clear all search history.
        
        Returns:
            Number of searches deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM searches")
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM results")
        cursor.execute("DELETE FROM searches")
        
        conn.commit()
        conn.close()
        
        return count
    
    def get_stats(self) -> Dict:
        """Get history statistics.
        
        Returns:
            Statistics dictionary
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM searches")
        total_searches = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM results")
        total_results = cursor.fetchone()[0]
        
        cursor.execute("SELECT topic, COUNT(*) as count FROM searches GROUP BY topic ORDER BY count DESC LIMIT 5")
        top_topics = cursor.fetchall()
        
        cursor.execute("SELECT source, COUNT(*) as count FROM results GROUP BY source ORDER BY count DESC LIMIT 5")
        top_sources = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_searches': total_searches,
            'total_results': total_results,
            'top_topics': [{'topic': t[0], 'count': t[1]} for t in top_topics],
            'top_sources': [{'source': s[0], 'count': s[1]} for s in top_sources]
        }
