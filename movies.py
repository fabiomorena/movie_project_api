# movies.py

import random
import movie_storage_sql
import requests
import os

# --- API Configuration ---
API_KEY = os.getenv('OMDB_API_KEY')
API_URL = "http://www.omdbapi.com/"

def list_movies():
    movies = movie_storage_sql.get_movies()
    print("\n***** Filme in der Datenbank *****")
    if not movies:
        print("Keine Filme in der Datenbank.")
    for title, data in movies.items():
        print(f"{title} ({data['jahr']}): {data['bewertung']:.1f}/10.0 - Poster: {data['poster_url']}")
    print(f"\nGesamtanzahl der Filme: {len(movies)}\n")

def add_movie():
    """
    Prompts for a movie title, fetches its data from OMDb, and adds it to the database.
    Handles API errors gracefully.
    """
    if not API_KEY:
        print("Fehler: OMDb API Key nicht gefunden. Bitte die Umgebungsvariable 'OMDB_API_KEY' setzen.")
        return

    while True:
        title_query = input("Filmtitel zum Hinzufügen: ").strip()
        if title_query:
            break
        print("Fehler: Der Filmtitel darf nicht leer sein.")

    movies = movie_storage_sql.get_movies()
    if any(title_query.lower() == existing.lower() for existing in movies.keys()):
        print("Dieser Film ist bereits in der Datenbank.")
        return

    # --- Fetch movie data from OMDb API with error handling ---
    params = {"t": title_query, "apikey": API_KEY}
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        movie_data = response.json()

        if movie_data.get("Response") == "False":
            print(f"Fehler: Film '{title_query}' wurde nicht gefunden. ({movie_data.get('Error')})")
            return

    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage. Bitte überprüfen Sie Ihre Internetverbindung. ({e})")
        return

    # Extract data from the API response
    title = movie_data.get("Title", "N/A")
    year = movie_data.get("Year", "N/A")
    poster_url = movie_data.get("Poster", "N/A")

    try:
        rating = float(movie_data.get("imdbRating", 0.0))
    except (ValueError, TypeError):
        rating = 0.0

    movie_storage_sql.add_movie(title, year, rating, poster_url)
    print(f"'{title}' ({year}) wurde mit einer Bewertung von {rating:.1f} hinzugefügt.\n")


def delete_movie():
    while True:
        title = input("Filmtitel zum Löschen: ").strip()
        if title:
            break
        print("Fehler: Der Filmtitel darf nicht leer sein.")

    movies = movie_storage_sql.get_movies()
    title_to_delete = None
    for key in movies.keys():
        if key.lower() == title.lower():
            title_to_delete = key
            break

    if title_to_delete:
        movie_storage_sql.delete_movie(title_to_delete)
        print(f"'{title_to_delete}' wurde gelöscht.\n")
    else:
        print("Film nicht gefunden.\n")

def update_movie():
    while True:
        title = input("Filmtitel zum Aktualisieren: ").strip()
        if title:
            break
        print("Fehler: Der Filmtitel darf nicht leer sein.")

    movies = movie_storage_sql.get_movies()
    title_to_update = None
    for key in movies.keys():
        if key.lower() == title.lower():
            title_to_update = key
            break

    if not title_to_update:
        print("Film nicht gefunden.\n")
        return

    while True:
        try:
            rating_str = input(f"Neue Bewertung für '{title_to_update}' (0.0–10.0): ")
            new_rating = float(rating_str)
            if 0.0 <= new_rating <= 10.0:
                break
            else:
                print("Fehler: Bitte eine Bewertung zwischen 0.0 und 10.0 eingeben.")
        except ValueError:
            print("Fehler: Ungültige Eingabe. Bitte eine Zahl eingeben.")

    movie_storage_sql.update_movie(title_to_update, new_rating)
    print(f"'{title_to_update}' wurde aktualisiert.\n")

def stats():
    movies = movie_storage_sql.get_movies()
    if not movies:
        print("Keine Filme in der Datenbank.\n")
        return

    ratings = [data['bewertung'] for data in movies.values()]
    avg = sum(ratings) / len(ratings)
    best_title = max(movies, key=lambda title: movies[title]['bewertung'])
    worst_title = min(movies, key=lambda title: movies[title]['bewertung'])

    print("\n***** Statistiken *****")
    print(f"Durchschnittliche Bewertung: {avg:.2f}")
    print(f"Bester Film: {best_title} ({movies[best_title]['bewertung']})")
    print(f"Schlechtester Film: {worst_title} ({movies[worst_title]['bewertung']})\n")

def random_movie():
    movies = movie_storage_sql.get_movies()
    if not movies:
        print("Keine Filme in der Datenbank.\n")
        return
    title = random.choice(list(movies.keys()))
    data = movies[title]
    print(f"Zufälliger Film: {title} ({data['jahr']}) - Bewertung: {data['bewertung']:.1f} - Poster: {data['poster_url']}\n")

def search_movie():
    movies = movie_storage_sql.get_movies()
    keyword = input("Suchbegriff: ").strip().lower()
    found_movies = []
    for title, data in movies.items():
        if keyword in title.lower():
            found_movies.append((title, data))

    if not found_movies:
        print("Kein passender Film gefunden.\n")
        return

    print("\nSuchergebnisse:")
    for title, data in found_movies:
        print(f"{title} ({data['jahr']}): {data['bewertung']:.1f}/10.0")
    print()


def sort_movies_by_rating():
    movies = movie_storage_sql.get_movies()
    if not movies:
        print("Keine Filme in der Datenbank.\n")
        return

    print("\n***** Filme sortiert nach Bewertung *****")
    sorted_movies = sorted(movies.items(), key=lambda item: item[1]['bewertung'], reverse=True)
    for title, data in sorted_movies:
        print(f"{title} ({data['jahr']}): {data['bewertung']:.1f}/10.0")
    print()

def generate_website():
    """Generates an index.html file from the movie data."""
    movies = movie_storage_sql.get_movies()
    if not movies:
        print("Keine Filme in der Datenbank, um eine Webseite zu erstellen.\n")
        return

    # Create the HTML content for each movie card
    movie_grid = ""
    for title, data in movies.items():
        movie_grid += f"""
        <div class="movie-card">
            <img class="movie-poster" src="{data['poster_url']}" alt="{title} Poster">
            <div class="movie-info">
                <h3 class="movie-title">{title} ({data['jahr']})</h3>
                <p class="movie-rating">Rating: {data['bewertung']:.1f} / 10</p>
            </div>
        </div>
        """

    # Full HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Meine Filmdatenbank</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 20px; }}
            h1 {{ text-align: center; color: #333; }}
            .movie-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }}
            .movie-card {{ background-color: white; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; }}
            .movie-poster {{ width: 100%; height: auto; }}
            .movie-info {{ padding: 15px; }}
            .movie-title {{ font-size: 1.2em; margin: 0 0 10px 0; }}
            .movie-rating {{ font-size: 1em; color: #666; margin: 0; }}
        </style>
    </head>
    <body>
        <h1>Meine Filmdatenbank</h1>
        <div class="movie-grid">
            {movie_grid}
        </div>
    </body>
    </html>
    """

    # Write the HTML content to a file
    try:
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(html_template)
        print("Website was generated successfully.\n")
    except IOError as e:
        print(f"Error writing to file: {e}\n")


def main():
    print("********** Meine Filmdatenbank **********")

    while True:
        # Updated menu with option 9
        print("""
Menu:
1. List movies
2. Add movie
3. Delete movie
4. Update movie
5. Stats
6. Random movie
7. Search movie
8. Movies sorted by rating
9. Generate website
0. Exit
""")
        # Updated input prompt
        choice = input("Wahl eingeben (1-9 oder 0): ")

        if choice == "1":
            list_movies()
        elif choice == "2":
            add_movie()
        elif choice == "3":
            delete_movie()
        elif choice == "4":
            update_movie()
        elif choice == "5":
            stats()
        elif choice == "6":
            random_movie()
        elif choice == "7":
            search_movie()
        elif choice == "8":
            sort_movies_by_rating()
        elif choice == "9": # <-- Added branch for the new command
            generate_website()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Ungültige Auswahl.\n")

if __name__ == "__main__":
    main()