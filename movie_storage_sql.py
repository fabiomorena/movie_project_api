# movie_storage_sql.py

import sqlite3

DB_FILE = "movie_database.db"


def _get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Creates the users and movies tables if they don't already exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Create a new table for users
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       name
                       TEXT
                       PRIMARY
                       KEY
                   )
                   """)
    # Add user_name column to movies table and create a composite primary key
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS movies
                   (
                       user_name
                       TEXT,
                       title
                       TEXT,
                       year
                       TEXT,
                       rating
                       REAL,
                       poster_url
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       user_name
                   ) REFERENCES users
                   (
                       name
                   ),
                       PRIMARY KEY
                   (
                       user_name,
                       title
                   )
                       )
                   """)
    conn.commit()
    conn.close()


# --- User Management Functions ---
def get_users():
    """Retrieves all users from the database."""
    create_tables()  # Ensure tables exist
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users ORDER BY name")
    users = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return users


def add_user(user_name):
    """Adds a new user to the database."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists, which is fine.
        pass
    finally:
        conn.close()


# --- Movie Management Functions (now user-aware) ---
def get_movies(user_name):
    """Retrieves all movies for a specific user."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE user_name = ?", (user_name,))

    movies_dict = {}
    for row in cursor.fetchall():
        movies_dict[row['title']] = {
            'jahr': row['year'],
            'bewertung': row['rating'],
            'poster_url': row['poster_url']
        }
    conn.close()
    return movies_dict


def add_movie(user_name, title, year, rating, poster_url):
    """Adds a new movie for a specific user."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movies (user_name, title, year, rating, poster_url) VALUES (?, ?, ?, ?, ?)",
                   (user_name, title, year, rating, poster_url))
    conn.commit()
    conn.close()


def delete_movie(user_name, title):
    """Deletes a movie for a specific user."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE user_name = ? AND title = ?", (user_name, title))
    conn.commit()
    conn.close()


def update_movie(user_name, title, new_rating):
    """Updates the rating of a movie for a specific user."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET rating = ? WHERE user_name = ? AND title = ?", (new_rating, user_name, title))
    conn.commit()
    conn.close()