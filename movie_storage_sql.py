# movie_storage_sql.py

import sqlite3

DB_FILE = "movie_database.db"


def _get_db_connection():
    """Establishes and returns a database connection."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    """Creates the movies table with a new poster_url column if it doesn't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Add the poster_url column to the table definition
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS movies
                   (
                       title
                       TEXT
                       PRIMARY
                       KEY,
                       year
                       TEXT,
                       rating
                       REAL,
                       poster_url
                       TEXT
                   )
                   """)
    conn.commit()
    conn.close()


# --- Functions called by the main script ---

def get_movies():
    """Retrieves all movies and returns them as a dictionary, including the poster URL."""
    create_table()
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")

    movies_dict = {}
    for row in cursor.fetchall():
        movies_dict[row['title']] = {
            'jahr': row['year'],
            'bewertung': row['rating'],
            'poster_url': row['poster_url']  # Add poster URL to the dictionary
        }

    conn.close()
    return movies_dict


def add_movie(title, year, rating, poster_url):
    """Adds a new movie to the database, including its poster URL."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    # Update INSERT statement to include the new field
    cursor.execute("INSERT INTO movies (title, year, rating, poster_url) VALUES (?, ?, ?, ?)",
                   (title, year, rating, poster_url))
    conn.commit()
    conn.close()


def delete_movie(title):
    """Deletes a movie from the database by its title."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE title = ?", (title,))
    conn.commit()
    conn.close()


def update_movie(title, new_rating):
    """Updates the rating of a movie in the database."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE movies SET rating = ? WHERE title = ?", (new_rating, title))
    conn.commit()
    conn.close()