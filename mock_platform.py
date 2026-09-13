import sqlite3
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Mock Instagram Platform", version="1.0")
DB_NAME = "mock_instagram.db"

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT NOT NULL,
        content TEXT NOT NULL,
        creative_brief TEXT NOT NULL,
        hashtags TEXT NOT NULL,
        time_posted TEXT NOT NULL,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        saves INTEGER DEFAULT 0
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        comment_text TEXT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Schemas ---
class PostCreate(BaseModel):
    channel: str  # "reel", "carousel", or "static"
    content: str
    creative_brief: str
    hashtags: List[str]
    time_posted: str  # e.g., "11:00"

# --- Hidden Rules Engine ---
def simulate_engagement(post: PostCreate):
    """
    Implements deterministic hidden rules based on content signals.
    """
    base_views = random.randint(1000, 3000)
    base_likes = int(base_views * 0.08)
    base_comments = random.randint(5, 25)
    base_saves = random.randint(10, 40)

    word_count = len(post.content.split())
    hashtag_count = len(post.hashtags)
    channel = post.channel.lower()

    # Rule 1: Reel length & caption rule
    if channel == "reel":
        if word_count <= 40:
            base_views = int(base_views * 1.5)  # Boost for short, snappy captions
        elif word_count > 80:
            base_views = int(base_views * 0.6)  # Penalty for text-heavy reels

    # Rule 2: Carousel Save trigger
    if channel == "carousel":
        if "save" in post.content.lower():
            base_saves = int(base_saves * 2.8)
            base_views = int(base_views * 1.3)

    # Rule 3: Hashtag spam penalty
    if hashtag_count > 8:
        base_views = int(base_views * 0.5)
        base_likes = int(base_likes * 0.5)
    elif 3 <= hashtag_count <= 5:
        base_views = int(base_views * 1.15)

    # Rule 4: Optimal posting window (10:00 - 12:00)
    hour = int(post.time_posted.split(":")[0]) if ":" in post.time_posted else 0
    if 10 <= hour <= 12:
        base_views = int(base_views * 1.25)
        base_likes = int(base_likes * 1.25)

    return base_views, base_likes, base_comments, base_saves

# --- API Endpoints ---
@app.post("/posts/publish")
def publish_post(post: PostCreate):
    views, likes, comments, saves = simulate_engagement(post)
    hashtags_str = ",".join(post.hashtags)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO posts (channel, content, creative_brief, hashtags, time_posted, views, likes, comments, saves)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (post.channel, post.content, post.creative_brief, hashtags_str, post.time_posted, views, likes, comments, saves))
    
    post_id = cursor.lastrowid

    # Seed mock comments based on post type so Community Agent has work to do
    mock_comment_pool = [
        "How much does this cost?",
        "Need this for my dorm setup!",
        "Does it come with a warranty?",
        "Love the aesthetic of this video!"
    ]
    for _ in range(min(comments, 2)):
        cursor.execute("""
            INSERT INTO user_comments (post_id, username, comment_text)
            VALUES (?, ?, ?)
        """, (post_id, f"student_{random.randint(100, 999)}", random.choice(mock_comment_pool)))

    conn.commit()
    conn.close()

    return {
        "status": "published",
        "post_id": post_id,
        "metrics": {"views": views, "likes": likes, "comments": comments, "saves": saves}
    }

@app.get("/posts")
def get_all_posts():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/posts/{post_id}/comments")
def get_comments(post_id: int):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_comments WHERE post_id = ?", (post_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
