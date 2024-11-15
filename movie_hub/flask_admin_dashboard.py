from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from config_db_admin import get_db 
from datetime import datetime

admin_bp = Blueprint("admin", __name__, template_folder="templates")


def insert_unique_value(table, column, value):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(f"""SELECT "ID" FROM {table} WHERE {column} = %s""", (value,))
    result = cursor.fetchone()

    if result:
        # print("\n\n", result, result[0], "\n\n")
        return result[0]
    else:
        cursor.execute(f"""SELECT COALESCE(MAX("ID"), 0) + 1 FROM {table}""")
        new_id = cursor.fetchone()[0]

        # Insert the new record with the calculated ID and the provided name
        cursor.execute(
            f"""INSERT INTO {table} ("ID", {column}) VALUES (%s, %s) """,
            (new_id, value),
        )
        db.commit()
    return new_id


@admin_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    # Ensure only admins can access
    if session.get("access_id") != 1:
        flash("Unauthorized access.", "error")
        return redirect(url_for("dashboard"))

    db = get_db()
    cursor = db.cursor()

    # Fetch data from movies
    cursor.execute("SELECT * FROM movies")
    movies_data = cursor.fetchall()

    return render_template("admin_dashboard.html", movies=movies_data)


@admin_bp.route("/add_movie", methods=["GET", "POST"])
@login_required
def add_movie():
    if request.method == "POST":
        # Get form data for the new movie
        movie_data = {
            "id": request.form.get("id"),
            "imdb_id": request.form.get("imdb_id"),
            "popularity": request.form.get("popularity"),
            "budget": request.form.get("budget"),
            "revenue": request.form.get("revenue"),
            "original_title": request.form.get("original_title"),
            "homepage": request.form.get("homepage"),
            "tagline": request.form.get("tagline"),
            "overview": request.form.get("overview"),
            "runtime": request.form.get("runtime"),
            "release_date": request.form.get("release_date"),
            "vote_count": request.form.get("vote_count"),
            "vote_average": request.form.get("vote_average"),
            "release_year": request.form.get("release_year"),
            "budget_adj": request.form.get("budget_adj"),
            "revenue_adj": request.form.get("revenue_adj"),
        }

        # Parse and handle multiple values
        production_companies = [
            company.strip()
            for company in request.form.get("production_companies", "").split(",")
        ]
        directors = [
            director.strip()
            for director in request.form.get("directors", "").split(",")
        ]
        genres = [genre.strip() for genre in request.form.get("genres", "").split(",")]
        actors = [actor.strip() for actor in request.form.get("actors", "").split(",")]
        keywords = [
            keyword.strip() for keyword in request.form.get("keywords", "").split(",")
        ]

        # Validate if movie ID is unique
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id FROM movies WHERE id = %s", (movie_data["id"],))
        if cursor.fetchone() is not None:
            flash("Movie ID already exists. Please use a unique ID.", "error")
            return redirect(url_for("add_movie"))

        # Convert release_date to the required format
        try:
            movie_data["release_date"] = datetime.strptime(
                movie_data["release_date"], "%Y-%m-%d"
            ).strftime("%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for("add_movie"))

        # Insert the new movie into the movies table
        cursor.execute(
            """
            INSERT INTO movies (id, imdb_id, popularity, budget, revenue, original_title, homepage,
                                tagline, overview, runtime, release_date, vote_count, vote_average,
                                release_year, budget_adj, revenue_adj)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                movie_data["id"],
                movie_data["imdb_id"],
                movie_data["popularity"],
                movie_data["budget"],
                movie_data["revenue"],
                movie_data["original_title"],
                movie_data["homepage"],
                movie_data["tagline"],
                movie_data["overview"],
                movie_data["runtime"],
                movie_data["release_date"],
                movie_data["vote_count"],
                movie_data["vote_average"],
                movie_data["release_year"],
                movie_data["budget_adj"],
                movie_data["revenue_adj"],
            ),
        )
        db.commit()

        # Helper function to insert values with uniqueness check

        # Insert directors, genres, actors, and production companies
        for director in directors:
            director_id = insert_unique_value("directors", '"Name"', director)
            # print(f"Inserting director ID {director_id} into movie_directors")
            cursor.execute(
                "INSERT INTO movie_directors (movie_id, director_id) VALUES (%s, %s)",
                (movie_data["id"], director_id),
            )
            db.commit()

        for genre in genres:
            genre_id = insert_unique_value("genres", '"Name"', genre)
            cursor.execute(
                "INSERT INTO movie_genres (movie_id, genre_id) VALUES (%s, %s)",
                (movie_data["id"], genre_id),
            )
            db.commit()

        for actor in actors:
            actor_id = insert_unique_value("actors", '"Name"', actor)
            cursor.execute(
                "INSERT INTO movie_actors (movie_id, actor_id) VALUES (%s, %s)",
                (movie_data["id"], actor_id),
            )
            db.commit()

        for company in production_companies:
            company_id = insert_unique_value("prod_companies", '"Name"', company)
            cursor.execute(
                "INSERT INTO movie_prod_companies (movie_id, prod_comp_id) VALUES (%s, %s)",
                (movie_data["id"], company_id),
            )
            db.commit()

        for keyword in keywords:
            keyword_id = insert_unique_value("keywords ", '"Name"', keyword)
            cursor.execute(
                "INSERT INTO movie_keywords (movie_id, keyword_id) VALUES (%s, %s)",
                (movie_data["id"], keyword_id),
            )
            db.commit()

        # db.commit()
        flash("Movie and associated data added successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("add_movie.html")


@admin_bp.route("/edit_movie/<int:id>", methods=["GET", "POST"])
@login_required
def edit_movie(id):
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        # Get form data
        updated_movie_data = {
            "imdb_id": request.form.get("imdb_id"),
            "popularity": request.form.get("popularity"),
            "budget": request.form.get("budget"),
            "revenue": request.form.get("revenue"),
            "original_title": request.form.get("original_title"),
            "homepage": request.form.get("homepage"),
            "tagline": request.form.get("tagline"),
            "overview": request.form.get("overview"),
            "runtime": request.form.get("runtime"),
            "release_date": request.form.get("release_date"),
            "vote_count": request.form.get("vote_count"),
            "vote_average": request.form.get("vote_average"),
            "release_year": request.form.get("release_year"),
            "budget_adj": request.form.get("budget_adj"),
            "revenue_adj": request.form.get("revenue_adj"),
        }

        # Parse and handle multiple values
        directors = [
            director.strip()
            for director in request.form.get("directors", "").split(",")
        ]
        genres = [genre.strip() for genre in request.form.get("genres", "").split(",")]
        actors = [actor.strip() for actor in request.form.get("actors", "").split(",")]
        production_companies = [
            company.strip()
            for company in request.form.get("production_companies", "").split(",")
        ]
        keywords = [
            keyword.strip() for keyword in request.form.get("keywords", "").split(",")
        ]

        # Update the movie in the movies table
        cursor.execute(
            """
            UPDATE movies SET imdb_id = %s, popularity = %s, budget = %s, revenue = %s, original_title = %s, 
                            homepage = %s, tagline = %s, overview = %s, runtime = %s, release_date = %s,
                            vote_count = %s, vote_average = %s, release_year = %s, budget_adj = %s, revenue_adj = %s
            WHERE id = %s
            """,
            (*updated_movie_data.values(), id),
        )
        db.commit()

        column_table_dict = {
            "director": "directors",
            "genre": "genres",
            "actor": "actors",
            "prod_comp": "prod_companies",
            "keyword": "keywords",
        }

        # Helper function for inserting/updating many-to-many relationships
        def update_association(table, column, values):
            cursor.execute(f"DELETE FROM {table} WHERE movie_id = %s", (id,))
            db.commit()
            for value in values:
                value_id = insert_unique_value(
                    column_table_dict[column], '"Name"', value
                )
                cursor.execute(
                    f"INSERT INTO {table} (movie_id, {column}_id) VALUES (%s, %s)",
                    (id, value_id),
                )
                db.commit()

        # Update related tables
        update_association("movie_directors", "director", directors)
        update_association("movie_genres", "genre", genres)
        update_association("movie_actors", "actor", actors)
        update_association("movie_prod_companies", "prod_comp", production_companies)
        update_association("movie_keywords", "keyword", keywords)

        flash("Movie updated successfully!", "success")
        return redirect(url_for("admin.admin_dashboard"))

    # Fetch the movie data to prefill the form
    cursor.execute("SELECT * FROM movies WHERE id = %s", (id,))
    movie_data = cursor.fetchone()
    # cursor.execute("SELECT "Name" FROM directors WHERE id = %s", (id,))
    # # movie_genre =
    # print("******\n\n", movie_data, "\n\n****\n")

    # Fetch related data for directors, genres, actors, production companies, and keywords
    cursor.execute(
        f"""SELECT directors."Name" FROM directors JOIN movie_directors 
        ON directors."ID" = movie_directors.director_id WHERE movie_id = %s""",
        (id,),
    )
    directors = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""SELECT genres."Name" FROM genres JOIN movie_genres ON 
        genres."ID" = movie_genres.genre_id WHERE movie_id = %s""",
        (id,),
    )
    genres = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""SELECT actors."Name" FROM actors JOIN movie_actors ON 
        actors."ID" = movie_actors.actor_id WHERE movie_id = %s""",
        (id,),
    )
    actors = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""SELECT prod_companies."Name" FROM prod_companies JOIN movie_prod_companies 
        ON prod_companies."ID" = movie_prod_companies.prod_comp_id WHERE movie_id = %s""",
        (id,),
    )
    production_companies = [row[0] for row in cursor.fetchall()]
    cursor.execute(
        f"""SELECT keywords."Name" FROM keywords JOIN movie_keywords 
        ON keywords."ID" = movie_keywords.keyword_id WHERE movie_id = %s""",
        (id,),
    )
    keywords = [row[0] for row in cursor.fetchall()]

    return render_template(
        "edit_movie.html",
        movie=movie_data,
        directors=",".join(directors),
        genres=",".join(genres),
        actors=",".join(actors),
        production_companies=",".join(production_companies),
        keywords=",".join(keywords),
    )


@admin_bp.route("/delete_movie/<int:id>", methods=["POST", "GET"])
@login_required
def delete_movie(id):
    db = get_db()
    cursor = db.cursor()

    # Start a transaction
    try:
        # Delete from related tables first to avoid foreign key constraint issues
        cursor.execute("DELETE FROM movie_prod_companies WHERE movie_id = %s", (id,))
        cursor.execute("DELETE FROM movie_directors WHERE movie_id = %s", (id,))
        cursor.execute("DELETE FROM movie_genres WHERE movie_id = %s", (id,))
        cursor.execute("DELETE FROM movie_actors WHERE movie_id = %s", (id,))
        cursor.execute("DELETE FROM movie_keywords WHERE movie_id = %s", (id,))

        # Delete from the main movies table
        cursor.execute("DELETE FROM movies WHERE id = %s", (id,))

        # Commit all deletions
        db.commit()

        flash("Movie and related entries deleted successfully!", "success")
    except Exception as e:
        # If there is an error, rollback the transaction
        db.rollback()
        flash("An error occurred while deleting the movie: " + str(e), "danger")
    finally:
        cursor.close()

    return redirect(url_for("admin.admin_dashboard"))
