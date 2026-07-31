import sqlite3

DB_NAME = "blogs.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT UNIQUE,
        title TEXT,
        content TEXT,
        status TEXT DEFAULT 'generated',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("PRAGMA table_info(blogs)")
    columns = [col[1] for col in cursor.fetchall()]

    if "status" not in columns:
        cursor.execute("ALTER TABLE blogs ADD COLUMN status TEXT DEFAULT 'generated'")


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blog_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blog_id INTEGER,
            topic TEXT,
            image_url TEXT NOT NULL,
            alt_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blog_id) REFERENCES blogs(id)
        )
        """)

    conn.commit()
    conn.close()

def save_blog(topic, title, content):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO blogs (topic, title, content) VALUES (?, ?, ?)",
            (topic, title, content)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # already exists

    conn.close()

def get_blog(topic):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, content FROM blogs WHERE topic = ?",
        (topic,)
    )

    result = cursor.fetchone()
    conn.close()

    return result if result else None

def get_all_blogs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, topic, title, status FROM blogs ORDER BY created_at DESC")

    blogs = cursor.fetchall()
    conn.close()

    return blogs

def update_status(blog_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE blogs SET status = ? WHERE id = ?",
        (status, blog_id)
    )

    conn.commit()
    conn.close()

def get_blog_by_id(blog_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT title, content FROM blogs WHERE id = ?",
        (blog_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result if result else None

def save_image_to_db(topic, image_url, alt_text):
    conn = sqlite3.connect("blogs.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO blog_images (topic, image_url, alt_text)
    VALUES (?, ?, ?)
    """, (topic, image_url, alt_text))

    conn.commit()
    conn.close()

def get_images_by_blog(blog_id):
    conn = sqlite3.connect("blogs.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT image_url, alt_text FROM blog_images
    WHERE blog_id = ?
    """, (blog_id,))

    images = cursor.fetchall()
    conn.close()

    return images


