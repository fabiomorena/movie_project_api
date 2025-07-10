# movies.py

import random
import movie_storage_sql
import requests
import os

# --- API Configuration ---
API_KEY = os.getenv('OMDB_API_KEY')
API_URL = "http://www.omdbapi.com/"


def list_movies(user_name):
    movies = movie_storage_sql.get_movies(user_name)
    print(f"\n***** Filme für {user_name} *****")
    if not movies:
        print("Keine Filme in der Datenbank.")
    for title, data in movies.items():
        print(f"{title} ({data['jahr']}): {data['bewertung']:.1f}/10.0 - Poster: {data['poster_url']}")
    print(f"\nGesamtanzahl der Filme: {len(movies)}\n")


def add_movie(user_name):
    if not API_KEY:
        print("Fehler: OMDb API Key nicht gefunden.")
        return

    title_query = input("Filmtitel zum Hinzufügen: ").strip()
    if not title_query:
        print("Fehler: Der Filmtitel darf nicht leer sein.")
        return

    movies = movie_storage_sql.get_movies(user_name)
    if any(title_query.lower() == existing.lower() for existing in movies.keys()):
        print("Dieser Film ist bereits in der Datenbank dieses Benutzers.")
        return

    params = {"t": title_query, "apikey": API_KEY}
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        movie_data = response.json()
        if movie_data.get("Response") == "False":
            print(f"Fehler: Film '{title_query}' wurde nicht gefunden.")
            return
    except requests.exceptions.RequestException as e:
        print(f"Fehler bei der API-Anfrage: {e}")
        return

    title = movie_data.get("Title", "N/A")
    year = movie_data.get("Year", "N/A")
    poster_url = movie_data.get("Poster", "N/A")
    try:
        rating = float(movie_data.get("imdbRating", 0.0))
    except (ValueError, TypeError):
        rating = 0.0

    movie_storage_sql.add_movie(user_name, title, year, rating, poster_url)
    print(f"'{title}' ({year}) wurde für {user_name} hinzugefügt.\n")


def delete_movie(user_name):
    title = input("Filmtitel zum Löschen: ").strip()
    if not title:
        print("Fehler: Der Filmtitel darf nicht leer sein.")
        return

    movies = movie_storage_sql.get_movies(user_name)
    title_to_delete = next((key for key in movies if key.lower() == title.lower()), None)

    if title_to_delete:
        movie_storage_sql.delete_movie(user_name, title_to_delete)
        print(f"'{title_to_delete}' wurde gelöscht.\n")
    else:
        print("Film nicht gefunden.\n")


def update_movie(user_name):
    title = input("Filmtitel zum Aktualisieren: ").strip()
    if not title:
        print("Fehler: Der Filmtitel darf nicht leer sein.")
        return

    movies = movie_storage_sql.get_movies(user_name)
    title_to_update = next((key for key in movies if key.lower() == title.lower()), None)

    if not title_to_update:
        print("Film nicht gefunden.\n")
        return

    try:
        rating_str = input(f"Neue Bewertung für '{title_to_update}' (0.0–10.0): ")
        new_rating = float(rating_str)
        if not (0.0 <= new_rating <= 10.0):
            print("Fehler: Bitte eine Bewertung zwischen 0.0 und 10.0 eingeben.")
            return
    except ValueError:
        print("Fehler: Ungültige Eingabe. Bitte eine Zahl eingeben.")
        return

    movie_storage_sql.update_movie(user_name, title_to_update, new_rating)
    print(f"'{title_to_update}' wurde aktualisiert.\n")


def stats(user_name):
    movies = movie_storage_sql.get_movies(user_name)
    if not movies:
        print("Keine Filme in der Datenbank für diesen Benutzer.\n")
        return

    ratings = [data['bewertung'] for data in movies.values()]
    avg = sum(ratings) / len(ratings)
    best_title = max(movies, key=lambda title: movies[title]['bewertung'])
    worst_title = min(movies, key=lambda title: movies[title]['bewertung'])

    print(f"\n***** Statistiken für {user_name} *****")
    print(f"Durchschnittliche Bewertung: {avg:.2f}")
    print(f"Bester Film: {best_title} ({movies[best_title]['bewertung']})")
    print(f"Schlechtester Film: {worst_title} ({movies[worst_title]['bewertung']})\n")


def random_movie(user_name):
    movies = movie_storage_sql.get_movies(user_name)
    if not movies:
        print("Keine Filme in der Datenbank für diesen Benutzer.\n")
        return
    title = random.choice(list(movies.keys()))
    data = movies[title]
    print(f"Zufälliger Film: {title} ({data['jahr']}) - Bewertung: {data['bewertung']:.1f}\n")


def generate_website(user_name):
    movies = movie_storage_sql.get_movies(user_name)
    if not movies:
        print(f"Keine Filme für {user_name}, um eine Webseite zu erstellen.\n")
        return

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

    html_template = f"""
    <!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><title>{user_name}'s Filme</title>
    <style>body{{font-family:sans-serif;background-color:#f4f4f4;}}h1{{text-align:center;}}
    .movie-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:20px;}}
    .movie-card{{background-color:white;border-radius:8px;box-shadow:0 4px 8px rgba(0,0,0,0.1);}}.movie-poster{{width:100%;}}
    .movie-info{{padding:15px;}}.movie-title{{font-size:1.2em;margin:0;}}.movie-rating{{color:#666;}}</style></head>
    <body><h1>{user_name}'s Filmdatenbank</h1><div class="movie-grid">{movie_grid}</div></body></html>"""

    # Save the website with the user's name
    file_name = f"{user_name}.html"
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(html_template)
        print(f"Webseite wurde erfolgreich als '{file_name}' generiert.\n")
    except IOError as e:
        print(f"Fehler beim Schreiben der Datei: {e}\n")


def user_login_or_create():
    """Handles user selection or creation and returns the active user's name."""
    while True:
        users = movie_storage_sql.get_users()
        print("\n********** Benutzerprofile **********")
        if users:
            for i, user in enumerate(users):
                print(f"{i + 1}. {user}")
        print("\n[N]euen Benutzer anlegen")
        print("[Q]uit")

        choice = input("Wahl: ").strip().lower()

        if choice == 'q':
            return None  # User wants to quit
        if choice == 'n':
            new_user = input("Neuen Benutzernamen eingeben: ").strip()
            if new_user:
                movie_storage_sql.add_user(new_user)
                return new_user
            else:
                print("Benutzername darf nicht leer sein.")
        elif choice.isdigit() and 1 <= int(choice) <= len(users):
            return users[int(choice) - 1]
        else:
            print("Ungültige Auswahl.")


def main():
    active_user = user_login_or_create()

    if not active_user:
        print("Bye!")
        return

    while True:
        print(f"\n--- Menu (Benutzer: {active_user}) ---")
        print("""1. Filme auflisten
2. Film hinzufügen
3. Film löschen
4. Filmbewertung aktualisieren
5. Statistiken anzeigen
6. Zufälligen Film anzeigen
7. Webseite generieren
8. Benutzer wechseln
0. Exit""")

        choice = input("Wahl eingeben: ")

        if choice == "1":
            list_movies(active_user)
        elif choice == "2":
            add_movie(active_user)
        elif choice == "3":
            delete_movie(active_user)
        elif choice == "4":
            update_movie(active_user)
        elif choice == "5":
            stats(active_user)
        elif choice == "6":
            random_movie(active_user)
        elif choice == "7":
            generate_website(active_user)
        elif choice == "8":
            new_user = user_login_or_create()
            if new_user:
                active_user = new_user
            else:  # User quit during selection
                break
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Ungültige Auswahl.\n")


if __name__ == "__main__":
    main()