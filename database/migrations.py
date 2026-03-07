"""
Database tables defined here.
"""

def run_migrations(db):
    """Creates the necessary tables if they don't exist."""
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS channel_stats (
                name TEXT,
                creation_date DATE,
                total_views INTEGER,
                total_subscribers INTEGER,
                total_videos INTEGER,
                last_updated DATE PRIMARY KEY
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_metrics (
                fetch_date DATE PRIMARY KEY,
                views INTEGER,
                subscribers_gained INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS video_metrics (
                video_id TEXT PRIMARY KEY,
                title TEXT,
                views INTEGER,
                subscribers_gained INTEGER
            )
        """)
        conn.commit()